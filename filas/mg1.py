"""
Modelo M/G/1: chegadas de Poisson, UM atendente e tempo de atendimento com distribuição QUALQUER.
Só é preciso conhecer a média (1/μ) e o desvio padrão σ do tempo de atendimento.

Fórmula de Pollaczek-Khintchine:
        Lq = (λ²σ² + ρ²) / (2(1 − ρ))        ρ = λ/μ
        Wq = Lq/λ     W = Wq + 1/μ     L = ρ + Lq     P0 = 1 − ρ

Casos particulares (σ em função de μ):
        exponencial (M/M/1)    σ = 1/μ
        constante   (M/D/1)    σ = 0
        Erlang-k    (M/Ek/1)   σ = 1/(μ·√k)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .modelos import FilaInstavel, Resultado


@dataclass(frozen=True)
class FilaMG1:
    """
    lam   : λ, chegadas por unidade de tempo.
    mu    : μ = 1 / (tempo médio de atendimento).
    sigma : desvio padrão do tempo de atendimento (mesma unidade de tempo de 1/μ).
            None = atendimento exponencial (σ = 1/μ), que acompanha μ quando ele muda.
    erlang_k : se informado, o atendimento é Erlang de k fases (σ = 1/(μ√k)), também acompanhando μ.
    """

    lam: float
    mu: float
    sigma: Optional[float] = None
    erlang_k: Optional[int] = None

    def __post_init__(self):
        if not self.lam > 0:
            raise ValueError("λ (taxa de chegada) precisa ser maior que zero.")
        if not self.mu > 0:
            raise ValueError("μ (taxa de atendimento) precisa ser maior que zero.")
        if self.sigma is not None and self.sigma < 0:
            raise ValueError("O desvio padrão σ não pode ser negativo.")
        if self.erlang_k is not None and (int(self.erlang_k) != self.erlang_k or self.erlang_k < 1):
            raise ValueError("k (nº de fases de Erlang) precisa ser um inteiro ≥ 1.")
        if self.lam >= self.mu:
            raise FilaInstavel(
                f"Fila instável: λ = {self.lam:g} é maior ou igual a μ = {self.mu:g}. "
                "Os clientes chegam mais rápido do que podem ser atendidos."
            )

    # ---- construtores para as distribuições mais comuns ---------------
    @classmethod
    def exponencial(cls, lam: float, mu: float) -> "FilaMG1":
        return cls(lam, mu, None)

    @classmethod
    def deterministica(cls, lam: float, mu: float) -> "FilaMG1":
        return cls(lam, mu, 0.0)

    @classmethod
    def erlang(cls, lam: float, mu: float, k: int) -> "FilaMG1":
        if int(k) != k or k < 1:
            raise ValueError("k (nº de fases de Erlang) precisa ser um inteiro ≥ 1.")
        return cls(lam, mu, None, int(k))

    # ---- interface parecida com a de Fila (usada pelo relatório) -----
    @property
    def s(self) -> int:
        return 1

    K = None
    N = None
    finita = False

    @property
    def familia(self) -> str:
        return "M/G/1"

    @property
    def nome(self) -> str:
        return "M/G/1"

    @property
    def sigma_efetivo(self) -> float:
        if self.erlang_k:
            return 1.0 / (self.mu * math.sqrt(self.erlang_k))
        return self.sigma if self.sigma is not None else 1.0 / self.mu

    @property
    def cv2(self) -> float:
        """Coeficiente de variação ao quadrado do atendimento: (σ·μ)². Vale 1 na exponencial, 0 na constante."""
        return (self.sigma_efetivo * self.mu) ** 2

    def resultado(self) -> Resultado:
        rho = self.lam / self.mu
        Lq = (self.lam ** 2 * self.sigma_efetivo ** 2 + rho ** 2) / (2.0 * (1.0 - rho))
        Wq = Lq / self.lam
        return Resultado(
            fila=self, rho=rho, P0=1.0 - rho, P_todos_ocupados=rho,
            L=rho + Lq, Lq=Lq, W=Wq + 1.0 / self.mu, Wq=Wq, lam_ef=self.lam,
            servidores_ocupados=rho,
        )
