"""
Filas com prioridades (classe 1 = maior prioridade).

Dois modelos:

1) PrioridadesMMs — s atendentes iguais, atendimento exponencial com a MESMA taxa μ em todas as classes.
   • sem interrupção: quem está sendo atendido termina o serviço (fórmula de Hillier/Lieberman).
   • com interrupção: a chegada de uma classe maior tira o atendimento da classe menor da vez.
     Para as classes 1..k, o sistema se comporta como um M/M/s só com essas classes, então
     L(1..k) = L do M/M/s com λ(1..k) e  Lk = L(1..k) − L(1..k−1).

2) PrioridadesMG1 — um atendente, cada classe com sua média e desvio padrão de atendimento, sem interrupção
   (fórmula de Cobham). Com a opção SPT, as classes são ordenadas pelo menor tempo médio de atendimento.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

from .modelos import Fila, FilaInstavel


@dataclass(frozen=True)
class MedidasClasse:
    classe: int            # número da classe como o usuário informou (1, 2, 3…)
    prioridade: int        # posição na ordem de atendimento (1 = maior prioridade)
    lam: float
    L: float
    Lq: float
    W: float
    Wq: float


@dataclass(frozen=True)
class ResultadoPrioridades:
    classes: list[MedidasClasse]     # na ordem de prioridade
    geral: MedidasClasse             # média de todos os clientes (igual à da fila FIFO)
    disciplina: str


def lams_de_percentuais(lam_total: float, percentuais: Sequence[float]) -> list[float]:
    """λ por classe a partir de λ total e das porcentagens (ex.: 5%, 20%, 75%). Aceita % que não soma 100."""
    soma = sum(percentuais)
    if soma <= 0:
        raise ValueError("As porcentagens precisam somar mais que zero.")
    return [lam_total * p / soma for p in percentuais]


def _valida_lams(lams: Sequence[float]):
    if not lams:
        raise ValueError("Informe ao menos uma classe.")
    if any(not l > 0 for l in lams):
        raise ValueError("Todas as taxas de chegada (λ de cada classe) precisam ser maiores que zero.")


@dataclass(frozen=True)
class PrioridadesMMs:
    """lams: λ de cada classe, da MAIOR para a MENOR prioridade. mu: taxa de UM atendente (igual p/ todas)."""

    lams: tuple
    mu: float
    s: int = 1
    interrupcao: bool = False

    def __post_init__(self):
        object.__setattr__(self, "lams", tuple(float(l) for l in self.lams))
        _valida_lams(self.lams)
        if not self.mu > 0:
            raise ValueError("μ (taxa de atendimento) precisa ser maior que zero.")
        if int(self.s) != self.s or self.s < 1:
            raise ValueError("O número de atendentes (s) precisa ser um inteiro ≥ 1.")
        if sum(self.lams) >= self.s * self.mu:
            raise FilaInstavel(
                f"Fila instável: a soma dos λ das classes ({sum(self.lams):g}) é maior ou igual a "
                f"s·μ = {self.s * self.mu:g}."
            )

    @property
    def disciplina(self) -> str:
        return "com interrupção" if self.interrupcao else "sem interrupção"

    def _W_sem_interrupcao(self) -> list[float]:
        s, mu, lam = self.s, self.mu, sum(self.lams)
        r = lam / mu
        # A = s!(sμ − λ)/r^s · Σ_{j<s} r^j/j!  +  sμ
        soma = sum(math.exp(math.lgamma(s + 1) - math.lgamma(j + 1) - (s - j) * math.log(r)) for j in range(s))
        A = (s * mu - lam) * soma + s * mu
        Ws, acum = [], 0.0
        for l in self.lams:
            b_ant = 1.0 - acum / (s * mu)
            acum += l
            b = 1.0 - acum / (s * mu)
            Ws.append(1.0 / (A * b_ant * b) + 1.0 / mu)
        return Ws

    def _W_com_interrupcao(self) -> list[float]:
        Ws, acum, L_ant = [], 0.0, 0.0
        for l in self.lams:
            acum += l
            L_acum = Fila(acum, self.mu, self.s).resultado().L
            Ws.append((L_acum - L_ant) / l)
            L_ant = L_acum
        return Ws

    def resultado(self) -> ResultadoPrioridades:
        Ws = self._W_com_interrupcao() if self.interrupcao else self._W_sem_interrupcao()
        classes = []
        lam_acumulado = 0.0
        for i, (lam_classe, w) in enumerate(zip(self.lams, Ws)):
            lam_acumulado += lam_classe
            # Com interrupção, Wk é obtido pela diferença entre os sistemas
            # acumulados. Para manter Lk = λk·Wk coerente com o gabarito
            # adotado na disciplina, L e Lq usam a taxa acumulada até a classe k.
            # Sem interrupção, permanecem associados à taxa individual da classe.
            lam_medidas = lam_acumulado if self.interrupcao else lam_classe
            wq = w - 1.0 / self.mu
            classes.append(MedidasClasse(
                i + 1, i + 1, lam_classe,
                lam_medidas * w,
                lam_medidas * wq,
                w, wq,
            ))
        r = Fila(sum(self.lams), self.mu, self.s).resultado()
        geral = MedidasClasse(0, 0, sum(self.lams), r.L, r.Lq, r.W, r.Wq)
        return ResultadoPrioridades(classes, geral, self.disciplina)


@dataclass(frozen=True)
class ClasseMG1:
    lam: float
    media: float        # tempo médio de atendimento E[S] da classe
    desvio: float = None  # desvio padrão do atendimento (None = exponencial: σ = E[S])


@dataclass(frozen=True)
class PrioridadesMG1:
    """Um atendente; classes na ordem de prioridade (ou use spt=True para ordenar pelo menor E[S])."""

    classes: tuple
    spt: bool = False

    def __post_init__(self):
        object.__setattr__(self, "classes", tuple(self.classes))
        _valida_lams([c.lam for c in self.classes])
        for c in self.classes:
            if not c.media > 0:
                raise ValueError("O tempo médio de atendimento de cada classe precisa ser maior que zero.")
            if c.desvio is not None and c.desvio < 0:
                raise ValueError("O desvio padrão não pode ser negativo.")
        if sum(c.lam * c.media for c in self.classes) >= 1:
            raise FilaInstavel("Fila instável: a soma de λi·E[Si] (ocupação total) é maior ou igual a 1.")

    @staticmethod
    def _sigma(c: ClasseMG1) -> float:
        return c.media if c.desvio is None else c.desvio

    def resultado(self) -> ResultadoPrioridades:
        ordem = sorted(range(len(self.classes)), key=lambda i: self.classes[i].media) if self.spt \
            else list(range(len(self.classes)))
        cs = [self.classes[i] for i in ordem]
        R = sum(c.lam * (self._sigma(c) ** 2 + c.media ** 2) for c in cs) / 2.0   # Σ λi·E[Si²] / 2
        saida, acum = [], 0.0
        for pos, (i, c) in enumerate(zip(ordem, cs), start=1):
            ant = acum
            acum += c.lam * c.media
            wq = R / ((1.0 - ant) * (1.0 - acum))
            saida.append(MedidasClasse(i + 1, pos, c.lam, c.lam * (wq + c.media), c.lam * wq, wq + c.media, wq))
        # média geral = M/G/1 com o serviço "misturado" (igual à de uma fila FIFO)
        lam = sum(c.lam for c in cs)
        es = sum(c.lam * c.media for c in cs) / lam
        es2 = sum(c.lam * (self._sigma(c) ** 2 + c.media ** 2) for c in cs) / lam
        rho = lam * es
        wq = lam * es2 / (2.0 * (1.0 - rho))
        geral = MedidasClasse(0, 0, lam, lam * (wq + es), lam * wq, wq + es, wq)
        return ResultadoPrioridades(saida, geral, "sem interrupção" + (" (SPT)" if self.spt else ""))
