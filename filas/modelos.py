"""
Núcleo de cálculo da Teoria das Filas para os modelos M/M.

Ideia central: todo modelo M/M é um "processo de nascimento e morte".
O sistema está no estado n (n clientes) e só pode ir para n+1 (chegada)
ou n-1 (saída). Basta definir duas taxas por estado:

    λn = taxa de chegada com n clientes no sistema
    μn = taxa de saída   com n clientes no sistema = min(n, s) · μ

e os seis modelos viram variações de uma mesma regra:

    Modelo        Servidores  Limite do sistema        λn
    M/M/1         1           nenhum                   λ
    M/M/s         s           nenhum                   λ
    M/M/1/K       1           K clientes no total      λ  (0 quando n = K)
    M/M/s/K       s           K clientes no total      λ  (0 quando n = K)
    M/M/1/N       1           população de N clientes  (N - n)·λ
    M/M/s/N       s           população de N clientes  (N - n)·λ

Uso rápido:

    from filas import Fila
    r = Fila(lam=3, mu=4).resultado()      # M/M/1
    print(r.L, r.W)                         # 3.0  1.0
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Optional

METRICAS = ("L", "Lq", "W", "Wq")


class FilaInstavel(ValueError):
    """λ >= s·μ em um modelo sem limite: a fila cresceria sem parar."""


class NaoDisponivel(ValueError):
    """Cálculo que não existe para o modelo escolhido."""


# --------------------------------------------------------------------------
# Resultado
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Resultado:
    """Todas as medidas de desempenho de uma fila (tempos na unidade de 1/λ e 1/μ)."""

    fila: "Fila"
    rho: float                 # taxa de ocupação por servidor = λef / (s·μ)
    P0: float                  # probabilidade do sistema vazio
    P_todos_ocupados: float    # P(n >= s): todos os servidores ocupados
    L: float                   # nº médio de clientes no sistema
    Lq: float                  # nº médio de clientes na fila
    W: float                   # tempo médio no sistema
    Wq: float                  # tempo médio na fila
    lam_ef: float              # taxa efetiva de chegada (clientes que entram)
    p_bloqueio: Optional[float] = None   # só modelos /K: P(n = K)
    lam_perdida: Optional[float] = None  # só modelos /K: clientes perdidos por tempo
    servidores_ocupados: Optional[float] = None  # nº médio de servidores ocupados = λef/μ
    n_operando: Optional[float] = None   # só modelos /N: N − L (clientes da população fora do sistema)
    disp_individual: Optional[float] = None  # só modelos /N: fração do tempo em que um cliente está fora (1 − L/N)
    rho_nominal: Optional[float] = None  # só modelos /N: N·λ/(s·μ), carga "de papel" da população (pode passar de 1)


# --------------------------------------------------------------------------
# Fila
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Fila:
    """
    Define uma fila M/M.

    lam : λ, chegadas por unidade de tempo.
          No modelo de população finita (N), é a taxa de CADA cliente que está fora.
    mu  : μ, atendimentos por unidade de tempo de UM servidor.
    s   : número de servidores (canais) em paralelo.
    K   : capacidade total do sistema (em atendimento + na fila). None = sem limite.
    N   : tamanho da população finita. None = população infinita.
    """

    lam: float
    mu: float
    s: int = 1
    K: Optional[int] = None
    N: Optional[int] = None

    def __post_init__(self):
        if not self.lam > 0:
            raise ValueError("λ (taxa de chegada) precisa ser maior que zero.")
        if not self.mu > 0:
            raise ValueError("μ (taxa de atendimento) precisa ser maior que zero.")
        if int(self.s) != self.s or self.s < 1:
            raise ValueError("O número de servidores (s) precisa ser um inteiro ≥ 1.")
        if self.K is not None and self.N is not None:
            raise ValueError("Use K (capacidade) ou N (população finita), não os dois.")
        if self.K is not None and (int(self.K) != self.K or self.K < self.s):
            raise ValueError(
                f"A capacidade K precisa ser um inteiro ≥ s (K={self.K}, s={self.s})."
            )
        if self.N is not None and (int(self.N) != self.N or self.N < 1):
            raise ValueError("A população N precisa ser um inteiro ≥ 1.")
        if self.K is None and self.N is None and self.lam >= self.s * self.mu:
            raise FilaInstavel(
                f"Fila instável: λ = {self.lam:g} é maior ou igual a s·μ = "
                f"{self.s * self.mu:g}. Os clientes chegam mais rápido do que "
                "podem ser atendidos, então a fila cresce sem parar. "
                "Aumente μ, aumente s ou reduza λ."
            )

    # ---- identificação do modelo -------------------------------------
    @property
    def familia(self) -> str:
        """Nome genérico do modelo, como nos slides (M/M/1, M/M/s, M/M/1/K ...)."""
        base = "M/M/1" if self.s == 1 else "M/M/s"
        if self.K is not None:
            return base + "/K"
        if self.N is not None:
            return base + "/N"
        return base

    @property
    def nome(self) -> str:
        """Nome com os números do problema, em notação de Kendall."""
        if self.K is not None:
            return f"M/M/{self.s}/{self.K}"
        if self.N is not None:
            return f"M/M/{self.s}/∞/{self.N}"
        return f"M/M/{self.s}"

    @property
    def finita(self) -> bool:
        return self.K is not None or self.N is not None

    @property
    def a(self) -> float:
        """Carga oferecida λ/μ (em erlangs)."""
        return self.lam / self.mu

    # ---- taxas por estado --------------------------------------------
    def _lam_n(self, n: int) -> float:
        if self.N is not None:
            return max(self.N - n, 0) * self.lam
        if self.K is not None and n >= self.K:
            return 0.0
        return self.lam

    def _mu_n(self, n: int) -> float:
        return min(n, self.s) * self.mu

    # ---- distribuição de probabilidade Pn ----------------------------
    @cached_property
    def _pn_finito(self) -> list[float]:
        """Pn para n = 0..M nos modelos finitos (usa logs para não estourar)."""
        M = self.K if self.K is not None else self.N
        logw = [0.0]
        for n in range(1, M + 1):
            logw.append(logw[-1] + math.log(self._lam_n(n - 1)) - math.log(self._mu_n(n)))
        topo = max(logw)
        w = [math.exp(x - topo) for x in logw]
        total = sum(w)
        return [x / total for x in w]

    @cached_property
    def _logD_infinito(self) -> float:
        """log do denominador de P0 (calculado em escala logarítmica: aguenta s na casa dos milhares)."""
        a, s = self.a, self.s
        la = math.log(a)
        termos = [n * la - math.lgamma(n + 1) for n in range(s)]
        termos.append(s * la - math.lgamma(s + 1) - math.log1p(-a / s))
        topo = max(termos)
        return topo + math.log(sum(math.exp(x - topo) for x in termos))

    @property
    def _P0_infinito(self) -> float:
        return math.exp(-self._logD_infinito)

    def P(self, n: int) -> float:
        """Probabilidade de haver exatamente n clientes no sistema."""
        if n < 0:
            return 0.0
        if self.finita:
            pn = self._pn_finito
            return pn[n] if n < len(pn) else 0.0
        a, s = self.a, self.s
        if n <= s:
            return math.exp(n * math.log(a) - math.lgamma(n + 1) - self._logD_infinito)
        return self.P(s) * (a / s) ** (n - s)

    def P_mais_que(self, r: int) -> float:
        """P(n > r): probabilidade de haver MAIS de r clientes no sistema."""
        if r < 0:
            return 1.0
        if self.finita:
            return sum(self._pn_finito[r + 1:])
        s = self.s
        if r >= s - 1:   # cauda geométrica (mais estável que 1 - soma)
            rho = self.a / s
            return self.P(s) * rho ** (r + 1 - s) / (1.0 - rho)
        return 1.0 - sum(self.P(n) for n in range(r + 1))

    def distribuicao(self, n_max: Optional[int] = None) -> list[float]:
        """Lista [P0, P1, ...]. Nos modelos sem limite, corta quando a cauda < 0,1%."""
        if self.finita:
            return list(self._pn_finito)
        if n_max is None:
            n_max = max(self.s + 4, 8)
            while self.P_mais_que(n_max) > 0.001 and n_max < 200:
                n_max += 1
        return [self.P(n) for n in range(n_max + 1)]

    # ---- medidas de desempenho ---------------------------------------
    def resultado(self) -> Resultado:
        if self.finita:
            return self._resultado_finito()
        return self._resultado_infinito()

    def _resultado_infinito(self) -> Resultado:
        s, rho = self.s, self.a / self.s
        p_espera = self.P(s) / (1.0 - rho)           # P(n >= s)  (Erlang C)
        Lq = p_espera * rho / (1.0 - rho)
        Wq = Lq / self.lam
        W = Wq + 1.0 / self.mu
        return Resultado(
            fila=self, rho=rho, P0=self._P0_infinito, P_todos_ocupados=p_espera,
            L=self.lam * W, Lq=Lq, W=W, Wq=Wq, lam_ef=self.lam,
            servidores_ocupados=self.a,
        )

    def _resultado_finito(self) -> Resultado:
        pn, s = self._pn_finito, self.s
        M = len(pn) - 1
        L = sum(n * p for n, p in enumerate(pn))
        Lq = sum((n - s) * p for n, p in enumerate(pn) if n > s)
        lam_ef = sum(self._lam_n(n) * p for n, p in enumerate(pn))
        bloqueio = pn[M] if self.K is not None else None
        return Resultado(
            fila=self, rho=lam_ef / (s * self.mu), P0=pn[0],
            P_todos_ocupados=sum(pn[s:]),
            L=L, Lq=Lq, W=L / lam_ef, Wq=Lq / lam_ef, lam_ef=lam_ef,
            p_bloqueio=bloqueio,
            lam_perdida=self.lam * bloqueio if bloqueio is not None else None,
            servidores_ocupados=lam_ef / self.mu,
            n_operando=(self.N - L) if self.N is not None else None,
            disp_individual=(1 - L / self.N) if self.N is not None else None,
            rho_nominal=(self.N * self.lam / (s * self.mu)) if self.N is not None else None,
        )

    # ---- consultas sobre o nº de clientes ----------------------------
    def P_clientes(self, op: str, a: int, b: Optional[int] = None) -> float:
        """
        Probabilidade sobre o nº de clientes no sistema.
        op: "=", "<", "≤", ">", "≥" (comparam n com a) ou "entre" (a ≤ n ≤ b).
        """
        a = int(a)
        if op == "=":
            r = self.P(a)
        elif op == ">":
            r = self.P_mais_que(a)
        elif op == "≥":
            r = self.P_mais_que(a - 1)
        elif op == "≤":
            r = 1.0 - self.P_mais_que(a)
        elif op == "<":
            r = 1.0 - self.P_mais_que(a - 1)
        elif op == "entre":
            if b is None or int(b) < a:
                raise ValueError("Em 'entre', o segundo valor precisa ser ≥ ao primeiro.")
            r = self.P_mais_que(a - 1) - self.P_mais_que(int(b))
        else:
            raise ValueError(f"Operador inválido: {op}")
        return min(1.0, max(0.0, r))

    def P_fila(self, op: str, a: int, b: Optional[int] = None) -> float:
        """Igual a P_clientes, mas sobre o nº de clientes ESPERANDO na fila (nq = max(n - s, 0))."""
        s, a = self.s, int(a)
        if op == "=":
            return self.P_clientes("≤", s) if a == 0 else (self.P(s + a) if a > 0 else 0.0)
        if op == "<":
            return 0.0 if a <= 0 else self.P_clientes("<", s + a)
        if op == "≤":
            return 0.0 if a < 0 else self.P_clientes("≤", s + a)
        if op == ">":
            return 1.0 if a < 0 else self.P_clientes(">", s + a)
        if op == "≥":
            return 1.0 if a <= 0 else self.P_clientes("≥", s + a)
        if op == "entre":
            if b is None or int(b) < a:
                raise ValueError("Em 'entre', o segundo valor precisa ser ≥ ao primeiro.")
            return min(1.0, max(0.0, self.P_fila("≥", a) - self.P_fila(">", int(b))))
        raise ValueError(f"Operador inválido: {op}")

    # ---- distribuição dos tempos de espera ---------------------------
    @cached_property
    def _vista_pela_chegada(self) -> list[float]:
        """
        Modelos finitos: probabilidade de um cliente que ENTRA encontrar n clientes no sistema
        (n = 0..M-1). É proporcional a λn·Pn (efeito PASTA ajustado pelas chegadas bloqueadas).
        """
        pn = self._pn_finito
        pesos = [self._lam_n(n) * pn[n] for n in range(len(pn) - 1)]
        total = sum(pesos)
        return [w / total for w in pesos]

    def P_Wq_maior(self, t: float) -> float:
        """P(Wq > t): probabilidade de esperar na fila mais que t."""
        if t < 0:
            return 1.0
        s, mu = self.s, self.mu
        if not self.finita:
            rho = self.a / s
            return self.P(s) / (1.0 - rho) * math.exp(-s * mu * (1.0 - rho) * t)
        # quem encontra n >= s clientes espera n-s+1 saídas, cada uma a taxa s·μ
        vista = self._vista_pela_chegada
        if len(vista) <= s:
            return 0.0
        F = _poisson_acumulada(s * mu * t, len(vista) - s)      # F[k] = P(Erlang(k, sμ) > t)
        return min(1.0, sum(vista[n] * F[n - s + 1] for n in range(s, len(vista))))

    def P_W_maior(self, t: float) -> float:
        """P(W > t): probabilidade de ficar no sistema (fila + serviço) mais que t."""
        if t < 0:
            return 1.0
        s, mu = self.s, self.mu
        if not self.finita:
            rho = self.a / s
            p_espera = self.P(s) / (1.0 - rho)
            x = s - 1 - self.a
            e1 = math.exp(-mu * t)
            if abs(x) < 1e-9:           # caso especial: o termo vira μ·t·e^(-μt)
                return e1 * (1.0 + p_espera * mu * t)
            e2 = math.exp(-mu * t * (s - self.a))
            return e1 + p_espera * (e1 - e2) / x
        vista = self._vista_pela_chegada
        n_max = len(vista) - 1
        if s == 1:                       # n clientes à frente + o próprio: Erlang(n+1, μ)
            F = _poisson_acumulada(mu * t, n_max + 1)
            return min(1.0, sum(p * F[n + 1] for n, p in enumerate(vista)))
        beta, gama = s * mu, (s - 1) * mu
        total = sum(vista[:s]) * math.exp(-mu * t)               # entra direto no serviço
        if n_max >= s:
            k_max = n_max - s + 1
            F = _poisson_acumulada(beta * t, k_max)
            sup = _poisson_superior(gama * t, k_max)
            razao = math.log(beta / gama)
            for n in range(s, n_max + 1):
                k = n - s + 1
                extra = (math.exp(-mu * t + k * razao + math.log(sup[k])) if sup[k] > 0 else 0.0)
                total += vista[n] * (F[k] + extra)
        return min(1.0, total)

    def tempo_percentil(self, p: float, variavel: str = "Wq") -> float:
        """
        Menor tempo t tal que P(X ≤ t) ≥ p, com X = "Wq" (espera na fila) ou "W" (tempo no sistema).
        Ex.: tempo_percentil(0.95, "Wq") -> "95% dos clientes esperam até t".
        """
        if not 0 < p < 1:
            raise ValueError("O percentil precisa estar entre 0 e 100% (exclusive).")
        cauda = {"Wq": self.P_Wq_maior, "W": self.P_W_maior}[variavel]
        alvo = 1.0 - p
        if cauda(0.0) <= alvo:
            return 0.0
        hi = 1.0 / self.mu
        for _ in range(200):
            if cauda(hi) <= alvo:
                break
            hi *= 2
        lo = 0.0
        for _ in range(200):
            meio = (lo + hi) / 2
            if cauda(meio) > alvo:
                lo = meio
            else:
                hi = meio
        return hi


# --------------------------------------------------------------------------
# Auxiliares numéricos (Erlang / Poisson)
# --------------------------------------------------------------------------
def _pmf_poisson(x: float, n: int) -> list[float]:
    """[P(Poisson(x) = j) para j = 0..n]."""
    if x <= 0:
        return [1.0] + [0.0] * n
    lx = math.log(x)
    return [math.exp(-x + j * lx - math.lgamma(j + 1)) for j in range(n + 1)]


def _poisson_acumulada(x: float, k_max: int) -> list[float]:
    """F[k] = P(Poisson(x) < k) = P(Erlang(k, β) > t) para k = 0..k_max (com x = β·t)."""
    pmf = _pmf_poisson(x, k_max)
    F, soma = [0.0], 0.0
    for j in range(k_max):
        soma += pmf[j]
        F.append(min(1.0, soma))
    return F


def _poisson_superior(x: float, k_max: int) -> list[float]:
    """sup[k] = P(Poisson(x) ≥ k) para k = 0..k_max, somando de trás para frente (estável)."""
    if x <= 0:
        return [1.0] + [0.0] * k_max
    j_max = max(k_max, int(x + 12 * math.sqrt(x) + 50))
    pmf = _pmf_poisson(x, j_max)
    sup, soma = [0.0] * (j_max + 2), 0.0
    for j in range(j_max, -1, -1):
        soma += pmf[j]
        sup[j] = soma
    return sup[:k_max + 1]


# --------------------------------------------------------------------------
# Ferramentas de dimensionamento
# --------------------------------------------------------------------------
def custo_total(res: Resultado, custo_servidor: float, custo_espera: float,
                espera_em: str = "L", custo_bloqueio: float = 0.0,
                servidor_so_ocupado: bool = False) -> float:
    """
    Custo por unidade de tempo = Cs·(servidores) + Cw·(L ou Lq) + Cb·(clientes perdidos).

    custo_servidor : custo de UM servidor por unidade de tempo.
    custo_espera   : custo de UM cliente esperando por unidade de tempo.
    espera_em      : "L" (cliente no sistema) ou "Lq" (cliente só na fila).
    custo_bloqueio : custo de cada cliente perdido (só modelos /K).
    servidor_so_ocupado : False = paga todos os s servidores o tempo todo (Cs·s);
                          True  = paga só enquanto trabalham (Cs · nº médio de servidores ocupados),
                          como no técnico que "pode ser realocado quando não está consertando".
    """
    if espera_em not in ("L", "Lq"):
        raise ValueError('espera_em deve ser "L" ou "Lq".')
    servidores = res.servidores_ocupados if servidor_so_ocupado else res.fila.s
    custo = custo_servidor * servidores + custo_espera * getattr(res, espera_em)
    if res.lam_perdida:
        custo += custo_bloqueio * res.lam_perdida
    return custo


def comparar_servidores(lam: float, mu: float, s_min: int = 1, s_max: int = 10,
                        K: Optional[int] = None, N: Optional[int] = None) -> list[Resultado]:
    """Resolve o mesmo problema para s = s_min..s_max (pula os casos instáveis)."""
    saida = []
    for s in range(s_min, s_max + 1):
        if K is not None and s > K:
            break
        try:
            saida.append(Fila(lam, mu, s, K, N).resultado())
        except FilaInstavel:
            continue
    return saida


def lambda_para_meta(fila: Fila, metrica: str, alvo: float) -> float:
    """
    Descobre o λ que faz a medida (L, Lq, W ou Wq) chegar ao valor `alvo`,
    mantendo μ, s, K e N da fila dada. Usa bisseção (as medidas só crescem com λ).
    """
    if metrica not in METRICAS:
        raise ValueError(f"Medida inválida: use uma entre {METRICAS}.")

    def f(lam):
        return getattr(Fila(lam, fila.mu, fila.s, fila.K, fila.N).resultado(), metrica) - alvo

    lo = fila.mu * 1e-9
    if f(lo) > 0:
        raise ValueError("A meta é menor que o mínimo possível para esse sistema.")
    if fila.finita:
        hi = fila.mu * fila.s
        for _ in range(60):
            if f(hi) >= 0:
                break
            hi *= 2
        else:
            raise ValueError("A meta não é alcançável para esse sistema.")
    else:
        hi = fila.s * fila.mu * (1 - 1e-9)
    for _ in range(200):
        meio = (lo + hi) / 2
        if f(meio) < 0:
            lo = meio
        else:
            hi = meio
    return (lo + hi) / 2


def menor_s_para_meta(lam: float, mu: float, metrica: str, alvo: float,
                      K: Optional[int] = None, N: Optional[int] = None,
                      s_max: int = 200) -> Optional[int]:
    """Menor número de servidores para que a medida (L, Lq, W ou Wq) fique ≤ alvo."""
    if metrica not in METRICAS:
        raise ValueError(f"Medida inválida: use uma entre {METRICAS}.")
    for res in comparar_servidores(lam, mu, 1, s_max, K, N):
        if getattr(res, metrica) <= alvo:
            return res.fila.s
    return None
