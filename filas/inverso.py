"""
Problemas "ao contrário": em vez de dar λ e μ e pedir as medidas, o enunciado dá medidas e pede um parâmetro.

  • resolver_por_medidas  : descobre λ e μ (M/M/1 ou M/M/s) a partir de DUAS medidas conhecidas
                            (ex.: ρ = 0,8 e Wq = 15 min; ou Lq = 3,2 e W = 0,5 h).
  • parametro_para_meta   : descobre λ ou μ para que uma medida (ou probabilidade) atinja um valor-meta.
  • menor_s_criterios     : menor nº de atendentes que cumpre vários critérios ao mesmo tempo.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

from .modelos import Fila, FilaInstavel

# --------------------------------------------------------------------------
# Catálogo de medidas que podem virar meta/critério
# --------------------------------------------------------------------------
# chave -> (descrição, tipo do argumento: None | "int" | "tempo")
MEDIDAS = {
    "L": ("nº médio de clientes no sistema (L)", None),
    "Lq": ("nº médio de clientes na fila (Lq)", None),
    "W": ("tempo médio no sistema (W)", None),
    "Wq": ("tempo médio na fila (Wq)", None),
    "rho": ("taxa de ocupação (ρ)", None),
    "P0": ("probabilidade de sistema vazio (P0)", None),
    "bloqueio": ("probabilidade de bloqueio (P_K)", None),
    "n>": ("P(mais de r clientes no sistema)", "int"),
    "n≥": ("P(r ou mais clientes no sistema)", "int"),
    "n≤": ("P(no máximo r clientes no sistema)", "int"),
    "n<": ("P(menos de r clientes no sistema)", "int"),
    "n=": ("P(exatamente r clientes no sistema)", "int"),
    "nq>": ("P(mais de r clientes na fila)", "int"),
    "nq≤": ("P(no máximo r clientes na fila)", "int"),
    "W>": ("P(tempo no sistema > t)", "tempo"),
    "W≤": ("P(tempo no sistema ≤ t)", "tempo"),
    "Wq>": ("P(tempo na fila > t)", "tempo"),
    "Wq≤": ("P(tempo na fila ≤ t)", "tempo"),
}


def avaliar(fila, tipo: str, arg: Optional[float] = None) -> float:
    """Valor da medida `tipo` (chave de MEDIDAS) para a fila dada."""
    if tipo not in MEDIDAS:
        raise ValueError(f"Medida desconhecida: {tipo}")
    if tipo in ("L", "Lq", "W", "Wq", "rho", "P0"):
        return getattr(fila.resultado(), tipo)
    if tipo == "bloqueio":
        p = fila.resultado().p_bloqueio
        if p is None:
            raise ValueError("A probabilidade de bloqueio só existe nos modelos com capacidade K.")
        return p
    if not hasattr(fila, "P_clientes"):
        raise ValueError("Essa medida só existe nos modelos M/M (não no M/G/1).")
    if tipo.startswith("nq"):
        return fila.P_fila(tipo[2:], int(arg))
    if tipo.startswith("n"):
        return fila.P_clientes(tipo[1:], int(arg))
    cauda = fila.P_W_maior if tipo.startswith("W>") or tipo.startswith("W≤") else fila.P_Wq_maior
    p = cauda(float(arg))
    return p if tipo.endswith(">") else 1.0 - p


def _com(fila, **mudancas):
    return replace(fila, **mudancas)


# --------------------------------------------------------------------------
# λ ou μ para atingir uma meta
# --------------------------------------------------------------------------
def parametro_para_meta(fila, parametro: str, tipo: str, alvo: float, arg: Optional[float] = None) -> float:
    """
    Descobre o valor de `parametro` ("lam" ou "mu") que faz a medida `tipo` valer `alvo`,
    mantendo todo o resto da fila. Funciona para M/M (todos os modelos) e M/G/1.
    Usa bisseção: a medida precisa ser monótona no parâmetro (é o caso de L, Lq, W, Wq, ρ e das probabilidades).
    """
    if parametro not in ("lam", "mu"):
        raise ValueError('O parâmetro precisa ser "lam" ou "mu".')
    mu0, lam0 = fila.mu, fila.lam
    s = getattr(fila, "s", 1)
    estavel_so = not fila.finita          # nos modelos sem limite, λ < s·μ é obrigatório

    def f(x):
        try:
            return avaliar(_com(fila, **{parametro: x}), tipo, arg) - alvo
        except FilaInstavel:
            return float("nan")

    if parametro == "lam":
        lo = mu0 * 1e-9
        hi = s * mu0 * (1 - 1e-9) if estavel_so else s * mu0
    else:
        lo = lam0 / s * (1 + 1e-9) if estavel_so else lam0 * 1e-9
        hi = max(2 * lam0 / s, lam0 * 2)
    f_lo, f_hi = f(lo), f(hi)
    if not estavel_so or parametro == "mu":
        for _ in range(60):                    # expande até a meta ficar entre os limites
            if f_lo * f_hi <= 0:
                break
            hi *= 2
            f_hi = f(hi)
    if f_lo != f_lo or f_hi != f_hi or f_lo * f_hi > 0:
        raise ValueError("Essa meta não pode ser atingida variando só esse parâmetro "
                         "(fora do intervalo possível para o sistema).")
    for _ in range(300):
        meio = (lo + hi) / 2
        f_meio = f(meio)
        if f_meio != f_meio:
            raise ValueError("O cálculo saiu da região estável do sistema.")
        if f_lo * f_meio <= 0:
            hi, f_hi = meio, f_meio
        else:
            lo, f_lo = meio, f_meio
    return (lo + hi) / 2


# --------------------------------------------------------------------------
# Vários critérios -> menor nº de atendentes
# --------------------------------------------------------------------------
def cumpre(valor: float, comparador: str, limite: float) -> bool:
    return valor <= limite + 1e-12 if comparador == "≤" else valor >= limite - 1e-12


def menor_s_criterios(lam: float, mu: float, criterios: list, K: Optional[int] = None,
                      N: Optional[int] = None, s_max: int = 200):
    """
    criterios: lista de (tipo, arg, comparador, limite), com comparador "≤" ou "≥".
    Ex.: [("Lq", None, "≤", 1), ("nq≤", 5, "≥", 0.95), ("Wq≤", 5, "≥", 0.95)]
    Devolve (s, linhas) com linhas = [(s, [valor de cada critério], cumpriu_todos)] para cada s testado,
    ou (None, linhas) se nenhum s até s_max cumprir tudo.
    """
    linhas = []
    for s in range(1, s_max + 1):
        if K is not None and s > K:
            break
        try:
            f = Fila(lam, mu, s, K, N)
        except FilaInstavel:
            continue
        valores = [avaliar(f, t, a) for t, a, _, _ in criterios]
        ok = all(cumpre(v, c, lim) for v, (_, _, c, lim) in zip(valores, criterios))
        linhas.append((s, valores, ok))
        if ok:
            return s, linhas
    return None, linhas


# --------------------------------------------------------------------------
# Descobrir λ e μ a partir de duas medidas conhecidas (M/M/1 e M/M/s sem limite)
# --------------------------------------------------------------------------
ADIMENSIONAIS = ("rho", "L", "Lq", "P0")     # só dependem de ρ (e de s)
TEMPOS = ("W", "Wq")                         # = (função de ρ) / μ
TAXAS = ("lam", "mu")
MEDIDAS_CONHECIDAS = {
    "rho": "taxa de ocupação (ρ)", "L": "nº médio no sistema (L)", "Lq": "nº médio na fila (Lq)",
    "P0": "probabilidade de sistema vazio (P0)", "W": "tempo médio no sistema (W)",
    "Wq": "tempo médio na fila (Wq)", "lam": "taxa de chegada (λ)", "mu": "taxa de atendimento (μ)",
}


def _normalizada(s: int, rho: float):
    """Resultado do M/M/s com μ = 1 e ρ dado (os tempos saem em unidades de 1/μ)."""
    return Fila(rho * s, 1.0, s).resultado()


def _valor_adim(tipo: str, res) -> float:
    return {"rho": res.rho, "L": res.L, "Lq": res.Lq, "P0": res.P0}[tipo]


def _mu_implicito(tipo: str, valor: float, rho: float, res, s: int) -> float:
    if tipo in TEMPOS:
        return getattr(res, tipo) / valor
    if tipo == "mu":
        return valor
    return valor / (rho * s)          # tipo == "lam"


def _raizes(f, tentativas=None) -> list[float]:
    """Raízes de f(ρ) = 0 em (0,1) por varredura de sinal + bisseção."""
    grade = sorted(set([i / 4000 for i in range(1, 4000)] + [1 - 10 ** (-k / 40) for k in range(160, 560)]))
    grade = [g for g in grade if 0 < g < 1]
    raizes, ant_x, ant_y = [], None, None
    for x in grade:
        try:
            y = f(x)
        except (FilaInstavel, ValueError, ZeroDivisionError, OverflowError):
            ant_x, ant_y = None, None
            continue
        if y == 0:
            raizes.append(x)
        elif ant_y is not None and ant_y * y < 0:
            lo, hi, f_lo = ant_x, x, ant_y
            for _ in range(200):
                m = (lo + hi) / 2
                fm = f(m)
                if f_lo * fm <= 0:
                    hi = m
                else:
                    lo, f_lo = m, fm
            raizes.append((lo + hi) / 2)
        ant_x, ant_y = x, y
    return raizes


def resolver_por_medidas(s: int, conhecidos: list) -> list:
    """
    s         : nº de atendentes (1 = M/M/1).
    conhecidos: duas medidas, [(tipo, valor), (tipo, valor)] com tipo em MEDIDAS_CONHECIDAS.
                Tempos (W, Wq) e taxas (λ, μ) precisam estar na MESMA unidade de tempo.
    Devolve a lista de soluções [(lam, mu)] (normalmente uma só).
    """
    if int(s) != s or s < 1:
        raise ValueError("O número de atendentes precisa ser um inteiro ≥ 1.")
    s = int(s)
    if len(conhecidos) != 2:
        raise ValueError("Informe exatamente duas medidas conhecidas.")
    (t1, v1), (t2, v2) = conhecidos
    for t, v in conhecidos:
        if t not in MEDIDAS_CONHECIDAS:
            raise ValueError(f"Medida desconhecida: {t}")
        if not v > 0:
            raise ValueError("Os valores informados precisam ser maiores que zero.")
    if t1 == t2:
        raise ValueError("Escolha duas medidas diferentes.")

    if {t1, t2} == {"lam", "mu"}:                                    # já dá λ e μ
        lam, mu = (v1, v2) if t1 == "lam" else (v2, v1)
        if lam >= s * mu:
            raise FilaInstavel("λ precisa ser menor que s·μ.")
        return [(lam, mu)]

    adim = [(t, v) for t, v in conhecidos if t in ADIMENSIONAIS]
    resto = [(t, v) for t, v in conhecidos if t not in ADIMENSIONAIS]
    if len(adim) == 2:
        raise ValueError("Essas duas medidas só dependem de ρ: falta uma medida com tempo ou taxa "
                         "(λ, μ, W ou Wq) para saber a escala.")
    if len(adim) == 1:
        (ta, va), (tb, vb) = adim[0], resto[0]
        raizes = _raizes(lambda r: _valor_adim(ta, _normalizada(s, r)) - va)
        saida = []
        for r in raizes:
            mu = _mu_implicito(tb, vb, r, _normalizada(s, r), s)
            saida.append((r * s * mu, mu))
    else:
        def diferenca(r):
            res = _normalizada(s, r)
            return _mu_implicito(t1, v1, r, res, s) - _mu_implicito(t2, v2, r, res, s)
        saida = []
        for r in _raizes(diferenca):
            mu = _mu_implicito(t1, v1, r, _normalizada(s, r), s)
            saida.append((r * s * mu, mu))
    if not saida:
        raise ValueError("Não existe um sistema estável com essas duas medidas. "
                         "Confira os valores e as unidades.")
    return saida
