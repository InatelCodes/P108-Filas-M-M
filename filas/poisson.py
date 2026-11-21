"""Contagens de Poisson: probabilidade de ocorrerem k eventos em um intervalo."""
from __future__ import annotations

import math


def media_no_intervalo(taxa: float, tempo: float) -> float:
    """Nº médio de eventos em `tempo` quando a taxa é `taxa` por unidade de tempo (mesma unidade)."""
    if taxa < 0 or tempo < 0:
        raise ValueError("Taxa e tempo não podem ser negativos.")
    return taxa * tempo


def pmf(k: int, media: float) -> float:
    """P(X = k) = e^(−m)·m^k / k!"""
    if k < 0:
        return 0.0
    if media == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-media + k * math.log(media) - math.lgamma(k + 1))


def cdf(k: int, media: float) -> float:
    """P(X ≤ k)"""
    return min(1.0, sum(pmf(j, media) for j in range(0, int(k) + 1))) if k >= 0 else 0.0


def probabilidade(op: str, k: int, media: float) -> float:
    """op: '=', '<', '≤', '>', '≥'."""
    k = int(k)
    if op == "=":
        return pmf(k, media)
    if op == "≤":
        return cdf(k, media)
    if op == "<":
        return cdf(k - 1, media)
    if op == ">":
        return max(0.0, 1.0 - cdf(k, media))
    if op == "≥":
        return max(0.0, 1.0 - cdf(k - 1, media))
    raise ValueError(f"Operador inválido: {op}")
