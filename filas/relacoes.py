"""
Relações gerais (valem para QUALQUER fila estável, sem supor exponencial):

    L  = λ·W         (Lei de Little)          Lq = λ·Wq
    W  = Wq + 1/μ                              L  = Lq + λ/μ

Servem quando o enunciado dá uma medida observada (ex.: "os clientes esperam em média 1 minuto")
e pede as outras, sem precisar do modelo M/M.
"""
from __future__ import annotations

from typing import Optional


def relacoes_de_little(lam: float, mu: float, L: Optional[float] = None, Lq: Optional[float] = None,
                       W: Optional[float] = None, Wq: Optional[float] = None) -> dict:
    """Dados λ, μ e UMA das medidas (L, Lq, W ou Wq), devolve as quatro. Tempos na mesma unidade de 1/λ."""
    dados = {k: v for k, v in dict(L=L, Lq=Lq, W=W, Wq=Wq).items() if v is not None}
    if len(dados) != 1:
        raise ValueError("Informe exatamente uma das medidas: L, Lq, W ou Wq.")
    if not lam > 0 or not mu > 0:
        raise ValueError("λ e μ precisam ser maiores que zero.")
    (nome, valor), = dados.items()
    if valor < 0:
        raise ValueError("A medida informada não pode ser negativa.")
    if nome == "Wq":
        wq = valor
    elif nome == "W":
        wq = valor - 1.0 / mu
    elif nome == "Lq":
        wq = valor / lam
    else:                                   # L
        wq = valor / lam - 1.0 / mu
    if wq < -1e-12:
        raise ValueError("Esse valor é impossível: o tempo na fila ficaria negativo "
                         "(o tempo no sistema precisa ser pelo menos 1/μ).")
    wq = max(wq, 0.0)
    w = wq + 1.0 / mu
    return {"L": lam * w, "Lq": lam * wq, "W": w, "Wq": wq}
