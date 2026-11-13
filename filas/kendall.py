"""
Decodificador da notação de Kendall  A/B/m/C/K/N

    A = distribuição das chegadas      B = distribuição do atendimento
    m = nº de servidores               C = disciplina da fila
    K = capacidade do sistema          N = tamanho da população

Aceita de 3 a 6 campos:  M/M/3  |  M/M/3/10  |  M/M/3/FCFS/10  |  M/M/3/FCFS/10/100
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_INFINITO = {"∞", "INF", "INFINITO", "INFINITY"}

DISCIPLINAS = {
    "FCFS": "FCFS/FIFO: o primeiro a chegar é o primeiro a ser servido",
    "FIFO": "FCFS/FIFO: o primeiro a chegar é o primeiro a ser servido",
    "LCFS": "LCFS/LIFO: o último a chegar é o primeiro a ser servido",
    "LIFO": "LCFS/LIFO: o último a chegar é o primeiro a ser servido",
    "SIRO": "SIRO: serviço em ordem aleatória",
}


def _distribuicao(codigo: str) -> str:
    c = codigo.upper()
    if c == "M":
        return "exponencial (Markoviana, sem memória)"
    if c == "D":
        return "determinística (tempo constante)"
    if c in ("G", "GI"):
        return "genérica"
    m = re.fullmatch(r"E([PK]?)(\d*)", c)
    if m:
        k = f" com k = {m.group(2)}" if m.group(2) else " (parâmetro de forma k)"
        return "Erlang" + k
    raise ValueError(f"Distribuição '{codigo}' não reconhecida (use M, D, Ek/Ep ou G).")


def _inteiro_ou_infinito(texto: str, campo: str) -> Optional[int]:
    t = texto.strip().upper()
    if t in _INFINITO:
        return None
    if not t.isdigit() or int(t) < 1:
        raise ValueError(f"{campo} inválido: '{texto}'. Use um inteiro positivo ou ∞.")
    return int(t)


@dataclass(frozen=True)
class Kendall:
    A: str
    B: str
    m: int
    disciplina: str = "FCFS"
    K: Optional[int] = None
    N: Optional[int] = None

    def explicar(self) -> list[str]:
        linhas = [
            f"Chegadas (A = {self.A}): distribuição {_distribuicao(self.A)}.",
            f"Atendimento (B = {self.B}): distribuição {_distribuicao(self.B)}.",
            f"Servidores (m = {self.m}): {self.m} canal(is) de serviço em paralelo.",
            "Disciplina: " + DISCIPLINAS.get(self.disciplina.upper(), f"{self.disciplina} (outra disciplina)."),
        ]
        if self.K is None:
            linhas.append("Capacidade (K = ∞): o sistema comporta qualquer número de clientes.")
        elif self.K < self.m:
            linhas.append(f"Capacidade (K = {self.K}): atenção, K menor que m deixaria servidores sem uso.")
        else:
            linhas.append(
                f"Capacidade (K = {self.K}): no máximo {self.K} clientes no sistema "
                f"({self.m} em atendimento + {self.K - self.m} na fila)."
            )
        if self.N is None:
            linhas.append("População (N = ∞): fonte infinita de clientes.")
        else:
            linhas.append(f"População (N = {self.N}): fonte finita com {self.N} clientes possíveis.")
        return linhas

    def modelo_do_projeto(self) -> tuple[Optional[dict], str]:
        """
        Diz se este projeto resolve a notação. Retorna (parametros, mensagem);
        parametros = {"s":..,"K":..,"N":..} para usar em Fila(lam, mu, **parametros).
        """
        if (self.A.upper(), self.B.upper()) != ("M", "M"):
            return None, ("Este projeto resolve só os modelos M/M (chegadas e atendimento "
                          "exponenciais). Para M/G/1 ou D/D/s, use outras fórmulas.")
        K, N = self.K, self.N
        if K is not None and N is not None:
            if K >= N:
                K = None  # o sistema comporta toda a população: é um modelo /N
            else:
                return None, ("Capacidade e população finitas ao mesmo tempo não são "
                              "tratadas aqui (só /K ou /N).")
        if K is not None and K < self.m:
            return None, "K precisa ser maior ou igual ao número de servidores."
        familia = ("M/M/1" if self.m == 1 else "M/M/s") + ("/K" if K else "/N" if N else "")
        return {"s": self.m, "K": K, "N": N}, f"Resolvido como o modelo {familia}."


def decodificar(notacao: str) -> Kendall:
    """'M/M/3/FCFS/10/100' -> objeto Kendall (use .explicar() para o texto)."""
    partes = [p.strip() for p in notacao.replace("\\", "/").split("/")]
    if not 3 <= len(partes) <= 6 or any(p == "" for p in partes):
        raise ValueError("Use de 3 a 6 campos separados por barra. Exemplo: M/M/3/FCFS/10/100")
    A, B = partes[0], partes[1]
    _distribuicao(A), _distribuicao(B)  # valida
    m = _inteiro_ou_infinito(partes[2], "Número de servidores")
    if m is None:
        raise ValueError("O número de servidores precisa ser finito.")
    disciplina, K, N = "FCFS", None, None
    resto = partes[3:]
    if len(resto) == 1:                                   # A/B/m/K  ou  A/B/m/C
        if resto[0].upper() in DISCIPLINAS:
            disciplina = resto[0].upper()
        else:
            K = _inteiro_ou_infinito(resto[0], "K")
    elif len(resto) == 2:                                 # A/B/m/C/K
        disciplina, K = resto[0].upper(), _inteiro_ou_infinito(resto[1], "K")
    elif len(resto) == 3:                                 # A/B/m/C/K/N
        disciplina = resto[0].upper()
        K, N = _inteiro_ou_infinito(resto[1], "K"), _inteiro_ou_infinito(resto[2], "N")
    return Kendall(A.upper(), B.upper(), m, disciplina, K, N)
