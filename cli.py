"""
Filas M/M no terminal.

    python cli.py                      menu interativo
    python cli.py calcular --lam 3 --mu 4
    python cli.py calcular --lam 12min --mu 8min --unidade hora
    python cli.py calcular --lam 2 --mu 0.7 --s 4 --unidade minuto
    python cli.py calcular --lam 5 --mu 4 --s 2 --K 10 --prob "nq>=2" "Wq<=5min" "p95:Wq"
    python cli.py kendall M/M/3/FCFS/10/100

    python cli.py calcular --lam 25 --mu 40 --sigma 0 --unidade hora        M/G/1 com atendimento constante
    python cli.py calcular --lam 25 --mu 40 --erlang 4                      M/G/1 com atendimento Erlang-4
    python cli.py prioridades --lams 0.1 0.4 1.5 --mu 3 --s 1 --interrupcao classes com prioridade
    python cli.py descobrir --s 1 --conhecido rho=0.8 Wq=15min --unidade hora   descobre λ e μ
    python cli.py poisson --taxa 12.8 --tempo 1 --prob "=10" "<=8"         contagens de Poisson
    python cli.py little --lam 40 --mu 30 --medida Wq=1min --unidade hora     lei de Little

Taxas aceitam um número (taxa, ex.: 3) ou um tempo médio (ex.: 20min, 40s, 1,5h).
"""
from __future__ import annotations

import argparse
import re
import sys

from filas import Fila, FilaInstavel
from filas.inverso import MEDIDAS_CONHECIDAS, resolver_por_medidas
from filas.mg1 import FilaMG1
from filas.poisson import media_no_intervalo, probabilidade as prob_poisson
from filas.prioridades import PrioridadesMMs
from filas.relacoes import relacoes_de_little
from filas.kendall import decodificar
from filas.relatorio import interpretar, linhas_resultado
from filas.unidades import (UNIDADES, converter_tempo, fmt, fmt_pct, fmt_tempo, ler_taxa,
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


_OPS = {"=": "=", "==": "=", "<": "<", "<=": "≤", "≤": "≤", ">": ">", ">=": "≥", "≥": "≥"}


def consultar_probabilidade(fila: Fila, unidade: str, comando: str) -> str:
    """
    Consultas (sem espaços ou com):
        n=3  n>5  n<=4  n>=2  n:2-6        nº de clientes no sistema
        nq=0  nq>2  nq<=1                  nº de clientes na fila
        W>12min  W<=1h  Wq>6min  Wq<=30s   tempos (sem unidade = unidade base)
        Wq=0                               chance de não esperar
        p95:Wq   p90:W                     percentil: tempo abaixo do qual ficam 95% / 90%
    """
    c = comando.replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"(nq|n)(=|==|<=|>=|<|>|≤|≥)(\d+)", c, re.I)
    if m:
        var, op, a = m.group(1).lower(), _OPS[m.group(2)], int(m.group(3))
        p = fila.P_fila(op, a) if var == "nq" else fila.P_clientes(op, a)
        nome = "nq" if var == "nq" else "n"
        return f"P({nome} {op} {a}) = {fmt(p, 6)}  ({fmt_pct(p)})"
    m = re.fullmatch(r"(nq|n):(\d+)-(\d+)", c, re.I)
    if m:
        var, a, b = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        p = fila.P_fila("entre", a, b) if var == "nq" else fila.P_clientes("entre", a, b)
        return f"P({a} ≤ {var} ≤ {b}) = {fmt(p, 6)}  ({fmt_pct(p)})"
    if re.fullmatch(r"wq=0", c, re.I):
        p = 1 - fila.P_Wq_maior(0.0)
        return f"P(Wq = 0) = {fmt(p, 6)}  ({fmt_pct(p)})  — chance de não esperar"
    m = re.fullmatch(r"(wq|w)(<=|≤|<|>)([\d.]+)([a-zçê]*)", c, re.I)
    if m:
        tipo, op, valor, un = m.group(1).lower(), m.group(2), float(m.group(3)), m.group(4)
        t = converter_tempo(valor, normalizar_unidade(un), unidade) if un else valor
        cauda = fila.P_Wq_maior(t) if tipo == "wq" else fila.P_W_maior(t)
        p = cauda if op == ">" else 1 - cauda
        simbolo = ">" if op == ">" else "≤"
        return (f"P({'Wq' if tipo == 'wq' else 'W'} {simbolo} {valor:g}{(' ' + un) if un else ''}) = "
                f"{fmt(p, 6)}  ({fmt_pct(p)})")
    m = re.fullmatch(r"p(\d+(?:\.\d+)?):(wq|w)", c, re.I)
    if m:
        pct, tipo = float(m.group(1)), m.group(2)
        t = fila.tempo_percentil(pct / 100, "Wq" if tipo.lower() == "wq" else "W")
        return f"{fmt(pct, 0)}% dos clientes têm {tipo.upper() if tipo.lower() == 'w' else 'Wq'} de até {fmt_tempo(t, unidade)}"
    raise ValueError("Consulta inválida. Exemplos: n=3 | n>=5 | n:2-6 | nq>2 | Wq>6min | W<=1h | Wq=0 | p95:Wq")


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
    print("\nConsultas (Enter para voltar). Ex.: n=3 | n>=5 | nq>2 | W>12min | Wq<=5min | Wq=0 | p95:Wq")
    while True:
        cmd = input("> ").strip()
        if not cmd:
            return
        try:
            print(" ", consultar_probabilidade(fila, unidade, cmd))
        except ValueError as e:
            print(f"  {e}")


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
        print("  1  Calculadora (M/M/1, M/M/s, /K, /N)\n  2  Decodificar notação de Kendall\n  0  Sair")
        opcao = input("Escolha: ").strip()
        try:
            if opcao == "1":
                fluxo_calculadora()
            elif opcao == "2":
                fluxo_kendall()
            elif opcao == "0":
                return
            else:
                print("Opção inválida.")
        except (ValueError, FilaInstavel) as e:
            print(f"\n⚠ {e}")


def _tempo_ou_numero(texto: str, unidade: str) -> float:
    """'15min' -> 15 minutos convertidos para a unidade base; '15' -> 15 na própria unidade base."""
    m = re.fullmatch(r"([\d.,]+)\s*([a-zçêé]*)", texto.strip(), re.I)
    if not m:
        raise ValueError(f"Valor inválido: '{texto}'. Exemplos: 15  |  15min  |  0,5h")
    valor = float(m.group(1).replace(",", "."))
    return valor if not m.group(2) else converter_tempo(valor, normalizar_unidade(m.group(2)), unidade)


def comando_descobrir(args):
    un = normalizar_unidade(args.unidade)
    conhecidos = []
    for item in args.conhecido:
        if "=" not in item:
            raise ValueError("Use medida=valor, por exemplo: rho=0.8 Wq=15min")
        chave, texto = item.split("=", 1)
        chave = chave.strip()
        if chave not in MEDIDAS_CONHECIDAS:
            raise ValueError(f"Medida '{chave}' desconhecida. Use: {', '.join(MEDIDAS_CONHECIDAS)}")
        if chave in ("lam", "mu"):
            valor = ler_taxa(texto, un)
        elif chave in ("W", "Wq"):
            valor = _tempo_ou_numero(texto, un)
        else:
            valor = float(texto.replace(",", ".")) / (100 if chave in ("rho", "P0") and float(texto.replace(",", ".")) > 1 else 1)
        conhecidos.append((chave, valor))
    solucoes = resolver_por_medidas(args.s, conhecidos)
    for lam, mu in solucoes:
        print(f"\nλ = {fmt(lam)} e μ = {fmt(mu)} por {un}")
        imprimir_resultado(Fila(lam, mu, args.s), un)


def comando_prioridades(args):
    un = normalizar_unidade(args.unidade)
    lams = [ler_taxa(x, un) for x in args.lams]
    mu = ler_taxa(args.mu, un)
    modelo = PrioridadesMMs(lams, mu, args.s, args.interrupcao)
    r = modelo.resultado()
    titulo(f"Prioridades {r.disciplina} — {args.s} atendente(s), μ = {fmt(mu)} por {un}")
    print(f"  {'Classe':<8}{'λ':>10}{'L':>10}{'Lq':>10}{'W':>14}{'Wq':>14}")
    for c in r.classes:
        print(f"  {c.classe:<8}{fmt(c.lam, 3):>10}{fmt(c.L):>10}{fmt(c.Lq):>10}{fmt_tempo(c.W, un):>14}{fmt_tempo(c.Wq, un):>14}")
    g = r.geral
    print(f"  {'Todos':<8}{fmt(g.lam, 3):>10}{fmt(g.L):>10}{fmt(g.Lq):>10}{fmt_tempo(g.W, un):>14}{fmt_tempo(g.Wq, un):>14}   (média = FIFO)")


def comando_poisson(args):
    un = normalizar_unidade(args.unidade)
    m = media_no_intervalo(ler_taxa(args.taxa, un), converter_tempo(float(args.tempo.replace(",", ".")), un, un))
    print(f"Média de eventos no intervalo: m = {fmt(m)}")
    for q in args.prob:
        mm = re.fullmatch(r"\s*(<=|>=|=|<|>|≤|≥)\s*(\d+)\s*", q)
        if not mm:
            raise ValueError("Consulta inválida. Exemplos: =10  <=8  >12")
        op = _OPS[mm.group(1)]
        print(f"  P(X {op} {mm.group(2)}) = {fmt(prob_poisson(op, int(mm.group(2)), m), 6)}")


def comando_little(args):
    un = normalizar_unidade(args.unidade)
    chave, texto = args.medida.split("=", 1)
    chave = chave.strip()
    if chave not in ("L", "Lq", "W", "Wq"):
        raise ValueError("A medida precisa ser L, Lq, W ou Wq. Exemplo: Wq=1min")
    valor = _tempo_ou_numero(texto, un) if chave in ("W", "Wq") else float(texto.replace(",", "."))
    d = relacoes_de_little(ler_taxa(args.lam, un), ler_taxa(args.mu, un), **{chave: valor})
    titulo("Lei de Little")
    print(f"  L  = {fmt(d['L'])} clientes\n  Lq = {fmt(d['Lq'])} clientes\n  W  = {fmt_tempo(d['W'], un)}\n  Wq = {fmt_tempo(d['Wq'], un)}")


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
    c.add_argument("--sigma", help="M/G/1: desvio padrão do atendimento (ex.: 0, 2min). Omita para exponencial")
    c.add_argument("--erlang", type=int, help="M/G/1: atendimento Erlang com k fases")
    c.add_argument("--prob", nargs="*", default=[], help="consultas: n=3 n>=5 n:2-6 nq>2 W>12min Wq<=5min Wq=0 p95:Wq")
    d = sub.add_parser("descobrir", help="descobre λ e μ a partir de duas medidas conhecidas")
    d.add_argument("--s", type=int, default=1)
    d.add_argument("--conhecido", nargs=2, required=True, help="duas medidas: rho=0.8 Wq=15min (rho, L, Lq, P0, W, Wq, lam, mu)")
    d.add_argument("--unidade", default="hora")
    pr = sub.add_parser("prioridades", help="fila com prioridades (M/M/s)")
    pr.add_argument("--lams", nargs="+", required=True, help="λ de cada classe, da maior para a menor prioridade")
    pr.add_argument("--mu", required=True)
    pr.add_argument("--s", type=int, default=1)
    pr.add_argument("--interrupcao", action="store_true", help="com interrupção (padrão: sem)")
    pr.add_argument("--unidade", default="hora")
    po = sub.add_parser("poisson", help="contagens de Poisson")
    po.add_argument("--taxa", required=True)
    po.add_argument("--tempo", default="1", help="tamanho do intervalo, na unidade escolhida")
    po.add_argument("--prob", nargs="+", default=[], help="consultas: =10 <=8 >12")
    po.add_argument("--unidade", default="hora")
    li = sub.add_parser("little", help="relações de Little (L=λW)")
    li.add_argument("--lam", required=True)
    li.add_argument("--mu", required=True)
    li.add_argument("--medida", required=True, help="uma medida conhecida: Wq=1min, W=3min, Lq=0.7, L=2")
    li.add_argument("--unidade", default="hora")
    k = sub.add_parser("kendall", help="decodifica uma notação de Kendall")
    k.add_argument("notacao")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "calcular":
            un = normalizar_unidade(args.unidade)
            if args.sigma is not None or args.erlang:
                sigma = None if args.sigma is None else _tempo_ou_numero(args.sigma, un)
                fila = FilaMG1(ler_taxa(args.lam, un), ler_taxa(args.mu, un), sigma, args.erlang)
            else:
                fila = Fila(ler_taxa(args.lam, un), ler_taxa(args.mu, un), args.s, args.K, args.N)
            imprimir_resultado(fila, un)
            for cmd in args.prob:
                print(" ", consultar_probabilidade(fila, un, cmd))
        elif args.cmd == "descobrir":
            comando_descobrir(args)
        elif args.cmd == "prioridades":
            comando_prioridades(args)
        elif args.cmd == "poisson":
            comando_poisson(args)
        elif args.cmd == "little":
            comando_little(args)
        elif args.cmd == "kendall":
            fluxo_kendall(args.notacao)
        else:
            menu()
    except (ValueError, FilaInstavel) as e:
        print(f"\n⚠ {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
