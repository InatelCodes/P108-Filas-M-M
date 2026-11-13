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
    def _P0_infinito(self) -> float:
        a, s = self.a, self.s
        rho = a / s
        soma, termo = 0.0, 1.0
        for n in range(s):          # soma de aⁿ/n!  para n = 0..s-1
            soma += termo
            termo *= a / (n + 1)    # ao final, termo = aˢ/s!
        return 1.0 / (soma + termo / (1.0 - rho))

    def P(self, n: int) -> float:
        """Probabilidade de haver exatamente n clientes no sistema."""
        if n < 0:
            return 0.0
        if self.finita:
            pn = self._pn_finito
            return pn[n] if n < len(pn) else 0.0
        a, s = self.a, self.s
        if n <= s:
            return self._P0_infinito * math.exp(n * math.log(a) - math.lgamma(n + 1))
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
        )

    # ---- distribuição dos tempos de espera (M/M/1 e M/M/s) -----------
    def _exige_infinita(self):
        if self.finita:
            raise NaoDisponivel(
                "P(W > t) e P(Wq > t) estão disponíveis apenas para M/M/1 e M/M/s "
                "(sem limite de capacidade e com população infinita)."
            )

    def P_Wq_maior(self, t: float) -> float:
        """P(Wq > t): probabilidade de esperar na fila mais que t."""
        self._exige_infinita()
        if t < 0:
            return 1.0
        rho = self.a / self.s
        p_espera = self.P(self.s) / (1.0 - rho)
        return p_espera * math.exp(-self.s * self.mu * (1.0 - rho) * t)

    def P_W_maior(self, t: float) -> float:
        """P(W > t): probabilidade de ficar no sistema (fila + serviço) mais que t."""
        self._exige_infinita()
        if t < 0:
            return 1.0
        s, mu = self.s, self.mu
        rho = self.a / s
        p_espera = self.P(s) / (1.0 - rho)
        x = s - 1 - self.a
        e1 = math.exp(-mu * t)
        if abs(x) < 1e-9:           # caso especial: o termo vira μ·t·e^(-μt)
            return e1 * (1.0 + p_espera * mu * t)
        e2 = math.exp(-mu * t * (s - self.a))
        return e1 + p_espera * (e1 - e2) / x


# --------------------------------------------------------------------------
# Ferramentas de dimensionamento
# --------------------------------------------------------------------------
def custo_total(res: Resultado, custo_servidor: float, custo_espera: float,
                espera_em: str = "L", custo_bloqueio: float = 0.0) -> float:
    """
    Custo por unidade de tempo = Cs·s + Cw·(L ou Lq) + Cb·(clientes perdidos).

    custo_servidor : custo de manter UM servidor por unidade de tempo.
    custo_espera   : custo de UM cliente esperando por unidade de tempo.
    espera_em      : "L" (cliente no sistema) ou "Lq" (cliente só na fila).
    custo_bloqueio : custo de cada cliente perdido (só modelos /K).
    """
    if espera_em not in ("L", "Lq"):
        raise ValueError('espera_em deve ser "L" ou "Lq".')
    custo = custo_servidor * res.fila.s + custo_espera * getattr(res, espera_em)
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
