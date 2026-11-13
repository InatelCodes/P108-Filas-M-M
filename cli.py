"""
Filas M/M no terminal.

    python cli.py                      menu interativo
    python cli.py calcular --lam 3 --mu 4
    python cli.py calcular --lam 20min --mu 15min --unidade hora
    python cli.py calcular --lam 0.6 --mu 0.5 --s 3 --unidade minuto
    python cli.py calcular --lam 5 --mu 4 --s 2 --K 10
    python cli.py exercicios           resolve todos os exercícios do PDF
    python cli.py kendall M/M/3/FCFS/10/100

Taxas aceitam um número (taxa, ex.: 3) ou um tempo médio (ex.: 20min, 40s, 1,5h).
"""
from __future__ import annotations

import argparse
import re
import sys

from filas import Fila, FilaInstavel, NaoDisponivel
from filas.exercicios import todos
from filas.kendall import decodificar
from filas.relatorio import interpretar, linhas_resultado
from filas.unidades import (UNIDADES, converter_tempo, fmt, fmt_pct, ler_taxa,
                            normalizar_unidade)


# ---- impressão -----------------------------------------------------------
def titulo(texto: str):
    print(f"\n{texto}\n{'─' * len(texto)}")


def imprimir_resultado(fila: Fila, unidade: str):
    res = fila.resultado()
    titulo(f"Modelo {fila.familia}  [{fila.nome}]   λ = {fmt(fila.lam)}  μ = {fmt(fila.mu)} por {unidade}")
    largura = max(len(n) for n, _ in linhas_resultado(res, unidade))
    for nome, valor in linhas_resultado(res, unidade):
        print(f"  {nome:<{largura}}  {valor}")
    print("\n" + interpretar(res, unidade))


def distribuicao(fila: Fila):
    titulo("Distribuição de probabilidade Pn")
    for n, p in enumerate(fila.distribuicao()):
        print(f"  P({n:>2}) = {fmt(p, 4)}  {'█' * round(p * 50)}")


def consultar_probabilidade(fila: Fila, unidade: str, comando: str) -> str:
    """Comandos: n=3 | n>5 | W>12min | Wq>6min | W>1 (sem unidade = unidade base)."""
    c = comando.replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"n=(\d+)", c, re.I)
    if m:
        n = int(m.group(1))
        return f"P(n = {n}) = {fmt(fila.P(n), 6)}"
    m = re.fullmatch(r"n>(\d+)", c, re.I)
    if m:
        r = int(m.group(1))
        return f"P(n > {r}) = {fmt(fila.P_mais_que(r), 6)}"
    m = re.fullmatch(r"(wq|w)>([\d.]+)([a-zçê]*)", c, re.I)
    if m:
        tipo, valor, un = m.group(1).lower(), float(m.group(2)), m.group(3)
        t = converter_tempo(valor, normalizar_unidade(un), unidade) if un else valor
        p = fila.P_Wq_maior(t) if tipo == "wq" else fila.P_W_maior(t)
        return f"P({'Wq' if tipo == 'wq' else 'W'} > {valor:g}{(' ' + un) if un else ''}) = {fmt(p, 6)}  ({fmt_pct(p)})"
    raise ValueError("Comando inválido. Exemplos: n=3 | n>5 | W>12min | Wq>6min")


# ---- fluxos --------------------------------------------------------------
def perguntar(texto: str, padrao: str = "") -> str:
    resp = input(f"{texto}{f' [{padrao}]' if padrao else ''}: ").strip()
    return resp or padrao


def fluxo_calculadora():
    titulo("Calculadora de filas M/M")
    unidade = normalizar_unidade(perguntar("Unidade de tempo (segundo, minuto, hora, dia, mês)", "hora"))
    s = int(perguntar("Quantos atendentes (servidores)?", "1"))
    print("Limite do sistema:  1 = sem limite   2 = capacidade máxima K   3 = população finita N")
    tipo = perguntar("Escolha", "1")
    K = N = None
    if tipo == "2":
        K = int(perguntar("K (máx. de clientes no sistema, incluindo quem está sendo atendido)"))
    elif tipo == "3":
        N = int(perguntar("N (tamanho da população)"))
    dica_lam = "taxa por cliente que está fora do sistema" if N else "chegadas"
    lam = ler_taxa(perguntar(f"λ — {dica_lam} por {unidade} (ex.: 3 ou 20min)"), unidade)
    mu = ler_taxa(perguntar(f"μ — atendimentos por {unidade}, de UM atendente (ex.: 4 ou 15min)"), unidade)
    fila = Fila(lam, mu, s, K, N)
    imprimir_resultado(fila, unidade)
    distribuicao(fila)
    print("\nProbabilidades extras (Enter para voltar). Ex.: n=3 | n>5 | W>12min | Wq>6min")
    while True:
        cmd = input("> ").strip()
        if not cmd:
            return
        try:
            print(" ", consultar_probabilidade(fila, unidade, cmd))
        except (ValueError, NaoDisponivel) as e:
            print(f"  {e}")


def fluxo_exercicios():
    for ex in todos():
        titulo(ex.titulo)
        print(ex.enunciado)
        print("Dados: " + " | ".join(f"{k} = {v}" for k, v in ex.dados.items()))
        for it in ex.itens:
            marca = {True: "✔", False: "✘", None: " "}[it.confere]
            print(f"  {marca} {it.letra:<7} {it.pergunta}")
            if it.tabela:
                print("      " + "  ".join(f"{c:<14}" for c in it.cabecalho))
                for linha in it.tabela:
                    print("      " + "  ".join(f"{str(c):<14}" for c in linha))
            else:
                extra = f"   (slide: {it.gabarito})" if it.gabarito else ""
                print(f"          = {it.resposta}{extra}")
        if ex.observacao:
            print(f"  Obs.: {ex.observacao}")


def fluxo_kendall(notacao: str | None = None):
    notacao = notacao or perguntar("Notação de Kendall (ex.: M/M/3/FCFS/10/100)")
    k = decodificar(notacao)
    titulo(f"Notação {notacao}")
    for linha in k.explicar():
        print("  • " + linha)
    print("\n" + k.modelo_do_projeto()[1])


def menu():
    while True:
        titulo("Teoria das Filas — modelos M/M")
        print("  1  Calculadora (M/M/1, M/M/s, /K, /N)\n  2  Exercícios do PDF resolvidos\n"
              "  3  Decodificar notação de Kendall\n  0  Sair")
        opcao = input("Escolha: ").strip()
        try:
            if opcao == "1":
                fluxo_calculadora()
            elif opcao == "2":
                fluxo_exercicios()
            elif opcao == "3":
                fluxo_kendall()
            elif opcao == "0":
                return
            else:
                print("Opção inválida.")
        except (ValueError, FilaInstavel) as e:
            print(f"\n⚠ {e}")


# ---- entrada -------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Filas M/M: M/M/1, M/M/s, M/M/1/K, M/M/s/K, M/M/1/N, M/M/s/N")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("calcular", help="resolve um sistema de filas")
    c.add_argument("--lam", required=True, help="λ: taxa (3) ou tempo médio entre chegadas (20min)")
    c.add_argument("--mu", required=True, help="μ: taxa (4) ou tempo médio de atendimento (15min)")
    c.add_argument("--s", type=int, default=1, help="nº de servidores (padrão 1)")
    c.add_argument("--K", type=int, help="capacidade máxima do sistema")
    c.add_argument("--N", type=int, help="tamanho da população finita")
    c.add_argument("--unidade", default="hora", help="unidade de tempo (padrão: hora)")
    c.add_argument("--prob", nargs="*", default=[], help="consultas: n=3 n>5 W>12min Wq>6min")
    sub.add_parser("exercicios", help="resolve os exercícios do PDF")
    k = sub.add_parser("kendall", help="decodifica uma notação de Kendall")
    k.add_argument("notacao")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "calcular":
            un = normalizar_unidade(args.unidade)
            fila = Fila(ler_taxa(args.lam, un), ler_taxa(args.mu, un), args.s, args.K, args.N)
            imprimir_resultado(fila, un)
            for cmd in args.prob:
                print(" ", consultar_probabilidade(fila, un, cmd))
        elif args.cmd == "exercicios":
            fluxo_exercicios()
        elif args.cmd == "kendall":
            fluxo_kendall(args.notacao)
        else:
            menu()
    except (ValueError, FilaInstavel, NaoDisponivel) as e:
        print(f"\n⚠ {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
