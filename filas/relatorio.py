"""Transforma um Resultado em linhas de texto legíveis (usado pelo app e pelo terminal)."""
from __future__ import annotations

from .modelos import Resultado
from .unidades import ABREV, PLURAL, fmt, fmt_pct, fmt_tempo


def _tempo(valor: float, unidade: str) -> str:
    """'45 min  (0,7500 horas)'; se já estiver na unidade base, só '0,7500 h'."""
    legivel = fmt_tempo(valor, unidade)
    if legivel.split()[-1] == ABREV[unidade]:
        return f"{fmt(valor)} {ABREV[unidade]}"
    return f"{legivel}  ({fmt(valor)} {PLURAL[unidade]})"


def linhas_resultado(res: Resultado, unidade: str) -> list[tuple[str, str]]:
    """Lista de (nome da medida, valor formatado)."""
    f = res.fila
    linhas = [
        ("Taxa de ocupação (ρ)", fmt_pct(res.rho)),
        ("Sistema vazio (P0)", fmt_pct(res.P0)),
        ("Sistema ocupado — P(n ≥ 1)" if f.s == 1 else f"Todos os {f.s} servidores ocupados — P(n ≥ s)",
         fmt_pct(res.P_todos_ocupados if f.s > 1 else 1 - res.P0)),
        ("Clientes no sistema (L)", fmt(res.L)),
        ("Clientes na fila (Lq)", fmt(res.Lq)),
        ("Tempo no sistema (W)", _tempo(res.W, unidade)),
        ("Tempo na fila (Wq)", _tempo(res.Wq, unidade)),
    ]
    if f.finita:
        linhas.append(("Taxa efetiva de chegada (λef)", f"{fmt(res.lam_ef)} clientes por {unidade}"))
    if res.p_bloqueio is not None:
        linhas.append(("Probabilidade de bloqueio (P_K)", fmt_pct(res.p_bloqueio)))
        linhas.append(("Clientes perdidos", f"{fmt(res.lam_perdida)} por {unidade}"))
    return linhas


def interpretar(res: Resultado, unidade: str) -> str:
    """Resumo em linguagem simples do que o resultado significa."""
    f = res.fila
    partes = [
        f"Em média há {fmt(res.L, 2)} clientes no sistema, sendo {fmt(res.Lq, 2)} esperando na fila.",
        f"Cada cliente espera {fmt_tempo(res.Wq, unidade)} na fila e permanece "
        f"{fmt_tempo(res.W, unidade)} no sistema.",
    ]
    if f.s == 1:
        partes.append(f"O atendente fica ocupado {fmt_pct(res.rho, 1)} do tempo.")
    else:
        partes.append(f"Cada um dos {f.s} servidores fica ocupado, em média, {fmt_pct(res.rho, 1)} do tempo.")
    if res.p_bloqueio is not None:
        partes.append(f"{fmt_pct(res.p_bloqueio)} dos clientes encontram o sistema cheio e vão embora.")
    return " ".join(partes)
