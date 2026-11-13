"""
Filas M/M — interface web.   Para abrir:   streamlit run app.py

Organização da tela: à ESQUERDA a "ficha" (o que você preenche, em passos numerados,
escrita como o enunciado); à DIREITA o resultado, que muda enquanto você digita.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from filas import (Fila, FilaInstavel, comparar_servidores, custo_total,
                   lambda_para_meta, menor_s_para_meta)
from filas.exercicios import todos as exercicios_do_pdf
from filas.kendall import decodificar
from filas.relatorio import interpretar, linhas_resultado
from filas.unidades import (PLURAL, UNIDADES, converter_taxa, converter_tempo, fmt, fmt_pct,
                            fmt_tempo, taxa_por_amostra, taxa_por_contagem, taxa_por_tempo_medio)

st.set_page_config(page_title="Filas M/M", page_icon=None, layout="wide")

# --------------------------------------------------------------------------
# Visual: papel, tinta e laranja de "senha de atendimento"
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root{--papel:#F3EEE3;--papel2:#FBF8F1;--tinta:#1F1D1A;--laranja:#D9480F;--cinza:#5E584D;--linha:#D8CFBB}
html,body,.stApp,.stApp p,.stApp label,.stApp li,.stApp button,.stApp input{font-family:'IBM Plex Sans',system-ui,sans-serif}
.stApp{background:var(--papel)}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:2rem;max-width:1320px}
.topo .olho{font:600 12px 'IBM Plex Mono',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--laranja)}
.topo .titulo{font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:2.7rem;line-height:1.05;margin:.2rem 0 .2rem;color:var(--tinta)}
.topo .sub{color:var(--cinza);margin-bottom:.8rem}
.stTabs [data-baseweb="tab-list"]{gap:2rem;border-bottom:2px solid var(--tinta)}
.stTabs [data-baseweb="tab"]{padding:.6rem 0;background:transparent}
.stTabs [data-baseweb="tab"] p{font:600 13px 'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:.09em}
.stTabs [aria-selected="true"] p{color:var(--laranja)}
.stTabs [data-baseweb="tab-highlight"]{background:var(--laranja);height:3px}
.stTabs [data-baseweb="tab-border"]{display:none}
.passo{display:flex;gap:12px;align-items:flex-start;margin:1.5rem 0 .55rem}
.passo .num{flex:none;width:28px;height:28px;border-radius:50%;background:var(--tinta);color:var(--papel);font:600 14px 'IBM Plex Mono',monospace;display:grid;place-items:center;margin-top:2px}
.passo .tit{font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:1.25rem;line-height:1.2;color:var(--tinta)}
.passo .dica{color:var(--cinza);font-size:.9rem;margin-top:2px}
.frase{padding-top:.5rem;font-size:1rem;line-height:1.3}
.eco{font:500 13px 'IBM Plex Mono',monospace;background:var(--papel2);border-left:3px solid var(--laranja);padding:7px 11px;margin:.35rem 0 0}
.modelo{font:500 13px 'IBM Plex Mono',monospace;border:1.5px dashed var(--tinta);padding:8px 12px;margin:.5rem 0 0;background:var(--papel2)}
.modelo b{color:var(--laranja);font-size:15px}
.tickets{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:.4rem 0 1rem}
.ticket{position:relative;background:var(--papel2);border:1.5px solid var(--tinta);padding:12px 14px 12px}
.ticket:before,.ticket:after{content:"";position:absolute;top:calc(50% - 7px);width:14px;height:14px;border-radius:50%;background:var(--papel);border:1.5px solid var(--tinta)}
.ticket:before{left:-8px;clip-path:inset(0 0 0 50%)}
.ticket:after{right:-8px;clip-path:inset(0 50% 0 0)}
.ticket .rot{font:600 11px 'IBM Plex Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--cinza)}
.ticket .val{font:600 28px/1.15 'IBM Plex Mono',monospace;color:var(--tinta);margin:4px 0 2px}
.ticket .sub{font-size:12px;color:var(--cinza)}
.nota{border-left:4px solid var(--laranja);background:var(--papel2);padding:12px 16px;margin:.2rem 0 1rem;line-height:1.5}
.aviso{border:1.5px solid var(--laranja);background:#FBE5D8;padding:12px 16px;line-height:1.5}
.vazio{border:1.5px dashed var(--cinza);padding:28px;color:var(--cinza);text-align:center}
.sec{font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:1.3rem;margin:1.6rem 0 .4rem;color:var(--tinta)}
.resp{font:600 22px 'IBM Plex Mono',monospace;padding-top:.15rem;color:var(--tinta)}
.resp small{font:500 12px 'IBM Plex Mono',monospace;color:var(--cinza);margin-left:6px}
.stMarkdown table{border-collapse:collapse;width:100%;font-size:.93rem}
.stMarkdown th{background:var(--tinta)!important;color:var(--papel)!important;font:600 11px 'IBM Plex Mono',monospace!important;letter-spacing:.06em;text-align:left;padding:7px 10px!important}
.stMarkdown td{border-bottom:1px solid var(--linha)!important;padding:7px 10px!important}
[data-testid="stExpander"]{border:1.5px solid var(--tinta);border-radius:2px;background:var(--papel2)}
[data-testid="stExpander"] summary p{font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:1.1rem}
@media (max-width:900px){.tickets{grid-template-columns:repeat(2,1fr)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------
METRICAS_UI = {
    "o tempo médio no sistema (W)": "W",
    "o tempo médio na fila (Wq)": "Wq",
    "o nº médio de clientes no sistema (L)": "L",
    "o nº médio de clientes na fila (Lq)": "Lq",
}
LIMITES = {
    "livre": "Sem limite — a fila pode crescer à vontade",
    "K": "Limite de K clientes — se estiver cheio, quem chega vai embora",
    "N": "Só existem N clientes no total (população finita)",
}

# textos das duas formas de dar o dado (o enunciado diz uma ou outra)
TXT_CHEGADA = {
    "tempo": dict(exemplo="“chega 1 cliente a cada 20 min”", antes="Chega 1 cliente a cada"),
    "taxa": dict(exemplo="“chegam 3 clientes por hora”", antes="Chegam", meio="clientes por"),
}
TXT_CHEGADA_N = {
    "tempo": dict(exemplo="“cada cliente volta a cada 10 h”", antes="Cada cliente fora do sistema volta a cada"),
    "taxa": dict(exemplo="“cada cliente volta 0,1 vez por hora”", antes="Cada cliente volta", meio="vez(es) por"),
}
TXT_ATEND = {
    "tempo": dict(exemplo="“cada atendimento leva 15 min”", antes="Cada atendimento leva"),
    "taxa": dict(exemplo="“cada atendente atende 4 clientes por hora”", antes="Cada atendente atende",
                 meio="clientes por"),
}
PAD_CHEGADA = {"tempo": (20.0, "minuto"), "taxa": (3.0, "hora")}
PAD_CHEGADA_N = {"tempo": (10.0, "hora"), "taxa": (0.1, "hora")}
PAD_ATEND = {"tempo": (15.0, "minuto"), "taxa": (4.0, "hora")}

# exemplos que preenchem a ficha inteira
EXEMPLOS = {
    "Barbearia — M/M/1 (slide)": dict(s=1, limite="livre", lam=("tempo", 20, "minuto"),
                                      mu=("tempo", 15, "minuto"), un="hora"),
    "Agência bancária, 3 caixas — M/M/s (slide)": dict(s=3, limite="livre", lam=("taxa", 0.6, "minuto"),
                                                       mu=("tempo", 2, "minuto"), un="minuto"),
    "Passar para 2 canais — M/M/s (slide)": dict(s=2, limite="livre", lam=("taxa", 30, "hora"),
                                                 mu=("taxa", 20, "hora"), un="minuto"),
    "Motores em manutenção — M/M/1 (slide)": dict(s=1, limite="livre", lam=("taxa", 11, "mês"),
                                                  mu=("taxa", 12.5, "mês"), un="dia"),
    "Barbearia com 4 lugares — M/M/1/K (exemplo extra)": dict(
        s=1, limite="K", K=4, lam=("tempo", 20, "minuto"), mu=("tempo", 15, "minuto"), un="hora"),
    "6 máquinas e 1 técnico — M/M/1/N (exemplo extra)": dict(
        s=1, limite="N", N=6, lam=("tempo", 10, "hora"), mu=("tempo", 2, "hora"), un="hora"),
}


# --------------------------------------------------------------------------
# Peças de interface
# --------------------------------------------------------------------------
def ini(chave: str, valor):
    """Valor inicial de um campo via estado da sessão (evita conflito com o botão de exemplos)."""
    st.session_state.setdefault(chave, valor)


def num(x: float, casas: int = 4) -> str:
    """Número sem zeros sobrando: 3,0000 -> 3."""
    return fmt(x, casas).rstrip("0").rstrip(",")


def md_tabela(cabecalho, linhas) -> str:
    topo = "| " + " | ".join(cabecalho) + " |\n|" + "---|" * len(cabecalho) + "\n"
    return topo + "\n".join("| " + " | ".join(str(c) for c in l) + " |" for l in linhas)


def html(texto: str):
    st.markdown(texto, unsafe_allow_html=True)


def passo(n: int, titulo: str, dica: str = ""):
    d = f'<div class="dica">{dica}</div>' if dica else ""
    html(f'<div class="passo"><span class="num">{n}</span><div><div class="tit">{titulo}</div>{d}</div></div>')


def frase(coluna, texto: str):
    coluna.markdown(f'<div class="frase">{texto}</div>', unsafe_allow_html=True)


def aviso(texto: str):
    html(f'<div class="aviso">{texto}</div>')


def vazio(texto: str):
    html(f'<div class="vazio">{texto}</div>')


def tickets(itens):
    corpo = "".join(f'<div class="ticket"><div class="rot">{r}</div><div class="val">{v}</div>'
                    f'<div class="sub">{s}</div></div>' for r, v, s in itens)
    html(f'<div class="tickets">{corpo}</div>')


def nome_modelo(s: int, limite: str) -> str:
    base = "M/M/1" if s == 1 else "M/M/s"
    return base + {"livre": "", "K": "/K", "N": "/N"}[limite]


def diagrama_svg(fila: Fila, rho: float) -> str:
    """Desenho do sistema: chegadas → fila → atendentes (mais forte = mais ocupado)."""
    n_serv = min(fila.s, 5)
    altura = max(96, 36 + n_serv * 34)
    meio = altura / 2
    cap_fila = (fila.K - fila.s) if fila.K else (fila.N - fila.s if fila.N else None)
    slots = 6 if cap_fila is None else max(0, min(cap_fila, 7))
    x_fim = 470
    partes = []
    for i in range(slots):
        x = x_fim - (i + 1) * 34
        partes.append(f'<rect x="{x}" y="{meio - 17}" width="28" height="34" fill="#FBF8F1" '
                      f'stroke="currentColor" stroke-width="1.5"/>')
    x_ini = x_fim - slots * 34
    if cap_fila is None or cap_fila > slots:
        partes.append(f'<text x="{x_ini - 8}" y="{meio + 5}" text-anchor="end" fill="currentColor" '
                      f'font-size="16">…</text>')
        x_ini -= 32
    rotulo = "sem espaço de fila" if slots == 0 else (
        "fila sem limite" if cap_fila is None else f"fila: cabem {cap_fila}")
    partes.append(f'<text x="{(x_ini + x_fim) / 2}" y="{meio + 36}" text-anchor="middle" fill="currentColor" '
                  f'fill-opacity=".7" font-size="12">{rotulo}</text>')
    origem = "população de N" if fila.N else "chegadas"
    xs = max(x_ini - 96, 10)
    partes.append(f'<text x="{xs}" y="{meio - 8}" fill="currentColor" font-size="13" font-weight="600">{origem}</text>')
    partes.append(f'<text x="{xs}" y="{meio + 12}" fill="currentColor" fill-opacity=".7" font-size="12">'
                  f'λ{" por cliente" if fila.N else ""}</text>')
    partes.append(f'<line x1="{xs + 72}" y1="{meio}" x2="{x_ini - 6}" y2="{meio}" stroke="currentColor"/>'
                  f'<polygon points="{x_ini - 6},{meio - 4} {x_ini + 2},{meio} {x_ini - 6},{meio + 4}" fill="currentColor"/>')
    cx = x_fim + 60
    partes.append(f'<line x1="{x_fim + 2}" y1="{meio}" x2="{cx - 18}" y2="{meio}" stroke="currentColor"/>')
    for i in range(n_serv):
        cy = meio + (i - (n_serv - 1) / 2) * 34
        partes.append(f'<circle cx="{cx}" cy="{cy}" r="13" fill="#D9480F" '
                      f'fill-opacity="{max(0.12, min(rho, 1)):.2f}" stroke="currentColor" stroke-width="1.5"/>')
    txt = f"{fila.s} atendente{'s' if fila.s > 1 else ''}" + (f" (mostrando {n_serv})" if fila.s > n_serv else "")
    partes.append(f'<text x="{cx + 26}" y="{meio - 4}" fill="currentColor" font-size="13" font-weight="600">{txt}</text>')
    partes.append(f'<text x="{cx + 26}" y="{meio + 14}" fill="currentColor" fill-opacity=".7" font-size="12">'
                  f'ocupação {fmt_pct(rho, 0)}</text>')
    dx = 10 - xs
    larg = cx + 200 + dx
    return (f'<svg viewBox="0 0 {larg:.0f} {altura}" width="100%" style="max-width:{larg:.0f}px;color:#1F1D1A" '
            f'font-family="IBM Plex Sans,sans-serif"><g transform="translate({dx},0)">{"".join(partes)}</g></svg>')


# --------------------------------------------------------------------------
# A ficha: passos 1, 2 e 3
# --------------------------------------------------------------------------
def cartao_taxa(chave: str, numero: int, titulo: str, ajuda: str, textos: dict, padroes: dict,
                simbolo: str):
    """Um campo escrito como frase do enunciado. Devolve a taxa por SEGUNDO (ou None)."""
    passo(numero, titulo, ajuda)
    modo = st.radio("O enunciado diz…", ["tempo", "taxa"], key=f"{chave}_modo",
                    format_func=lambda m: textos[m]["exemplo"])
    t = textos[modo]
    valor0, un0 = padroes[modo]
    k_val, k_un = f"{chave}_valor_{modo}", f"{chave}_un_{modo}"
    ini(k_val, valor0)
    ini(k_un, un0)
    if modo == "tempo":
        c1, c2, c3 = st.columns([3.4, 1.3, 1.7])
        frase(c1, t["antes"])
        valor = c2.number_input("valor", min_value=0.0, step=1.0, format="%g",
                                key=k_val, label_visibility="collapsed")
        unid = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=k_un,
                            label_visibility="collapsed")
    else:
        c1, c2, c3, c4 = st.columns([2.3, 1.2, 1.7, 1.5])
        frase(c1, t["antes"])
        valor = c2.number_input("valor", min_value=0.0, step=0.1, format="%g",
                                key=k_val, label_visibility="collapsed")
        frase(c3, t["meio"])
        unid = c4.selectbox("unidade", list(UNIDADES), key=k_un, label_visibility="collapsed")
    if valor <= 0:
        html('<div class="eco">Digite um valor maior que zero.</div>')
        return None
    taxa_s = (taxa_por_tempo_medio(converter_tempo(valor, unid, "segundo")) if modo == "tempo"
              else converter_taxa(valor, unid, "segundo"))
    html(f'<div class="eco">{simbolo} = {num(taxa_s * 3600)} por hora &nbsp;·&nbsp; '
         f'1 a cada {fmt_tempo(1 / taxa_s, "segundo")}</div>')
    return taxa_s


def formulario(chave: str, variar_s: bool = False, pedir_lam: bool = True, com_exemplos: bool = False):
    """
    Monta a ficha. Devolve dict(lam, mu, s, K, N, unidade) ou None se faltar dado.
    variar_s=True  -> o nº de atendentes não é perguntado (a ferramenta testa vários).
    pedir_lam=False -> λ não é perguntado (a ferramenta descobre λ).
    """
    if com_exemplos:
        st.selectbox("Comece por um exemplo (preenche tudo)", ["— escolha —"] + list(EXEMPLOS),
                     key=f"{chave}_exemplo", on_change=_carregar_exemplo, args=(chave,))

    # ---- passo 1: o sistema
    passo(1, "Como é o seu sistema?", "Responda olhando o enunciado.")
    s = 1
    if not variar_s:
        ini(f"{chave}_s", 1)
        s = st.number_input("Quantos atendentes trabalham ao mesmo tempo? (caixas, guichês, barbeiros…)",
                            min_value=1, step=1, key=f"{chave}_s")
    limite = st.radio("Quantos clientes cabem no sistema?", list(LIMITES), format_func=LIMITES.get,
                      key=f"{chave}_limite")
    K = N = None
    if limite == "K":
        ini(f"{chave}_K", 10)
        K = st.number_input("K = máximo de clientes no sistema (conta quem está sendo atendido + a fila)",
                            min_value=1, step=1, key=f"{chave}_K")
    elif limite == "N":
        ini(f"{chave}_N", 20)
        N = st.number_input("N = quantos clientes existem no total", min_value=1, step=1,
                            key=f"{chave}_N")
    if not variar_s:
        extra = f" · K = {int(K)}" if K else (f" · N = {int(N)}" if N else "")
        html(f'<div class="modelo">Modelo: <b>{nome_modelo(int(s), limite)}</b>'
             f'&nbsp;({int(s)} atendente{"s" if s > 1 else ""}{extra})</div>')
    else:
        html(f'<div class="modelo">Modelo: <b>M/M/s{"" if limite == "livre" else "/" + limite}</b>'
             '&nbsp;(o nº de atendentes será testado)</div>')

    # ---- passos 2 e 3: taxas
    numero = 2
    lam_s = 1.0
    if pedir_lam:
        if limite == "N":
            lam_s = cartao_taxa(f"{chave}_lamN", numero, "Com que frequência os clientes voltam?",
                                "Aqui λ é de CADA cliente que está fora do sistema.", TXT_CHEGADA_N,
                                PAD_CHEGADA_N, "λ por cliente")
        else:
            lam_s = cartao_taxa(f"{chave}_lam", numero, "Quanto chega?",
                                "É a taxa de chegada, λ.", TXT_CHEGADA, PAD_CHEGADA, "λ")
        numero += 1
    mu_s = cartao_taxa(f"{chave}_mu", numero, "Quanto cada atendente atende?",
                       "É a taxa de atendimento, μ — de UM atendente.", TXT_ATEND, PAD_ATEND, "μ")

    html('<div style="height:.9rem"></div>')
    ini(f"{chave}_unidade", "hora")
    unidade = st.selectbox("Mostrar os tempos do resultado em", list(UNIDADES),
                           format_func=lambda u: PLURAL[u], key=f"{chave}_unidade")
    if lam_s is None or mu_s is None:
        return None
    return dict(lam=lam_s * UNIDADES[unidade], mu=mu_s * UNIDADES[unidade], s=int(s),
                K=int(K) if K else None, N=int(N) if N else None, unidade=unidade)


def _carregar_exemplo(chave: str):
    ex = EXEMPLOS.get(st.session_state.get(f"{chave}_exemplo"))
    if not ex:
        return
    ss = st.session_state
    ss[f"{chave}_s"] = ex["s"]
    ss[f"{chave}_limite"] = ex["limite"]
    if ex.get("K"):
        ss[f"{chave}_K"] = ex["K"]
    if ex.get("N"):
        ss[f"{chave}_N"] = ex["N"]
    k_lam = f"{chave}_lamN" if ex["limite"] == "N" else f"{chave}_lam"
    for k, (modo, valor, un) in ((k_lam, ex["lam"]), (f"{chave}_mu", ex["mu"])):
        ss[f"{k}_modo"] = modo
        ss[f"{k}_valor_{modo}"] = float(valor)
        ss[f"{k}_un_{modo}"] = un
    ss[f"{chave}_unidade"] = ex["un"]


def construir_fila(p: dict):
    try:
        return Fila(p["lam"], p["mu"], p["s"], p["K"], p["N"])
    except ValueError as e:     # inclui FilaInstavel
        aviso(f"<b>Não dá para calcular:</b> {e}")
    return None


def passo_meta(chave: str, numero: int, unidade: str):
    """Frase: 'Quero que [medida] fique em até [valor] [unidade]'. Devolve (metrica, alvo na unidade base)."""
    passo(numero, "Qual é a meta?", "Escolha a medida e o valor máximo aceitável.")
    rotulo = st.selectbox("Quero que…", list(METRICAS_UI), key=f"{chave}_met")
    metrica = METRICAS_UI[rotulo]
    eh_tempo = metrica in ("W", "Wq")
    c1, c2 = st.columns([1, 1.4])
    ini(f"{chave}_alvo", 1.0)
    alvo = c1.number_input("fique em até", min_value=0.0, step=0.1, format="%g", key=f"{chave}_alvo")
    if eh_tempo:
        ini(f"{chave}_unalvo", unidade)
        un = c2.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=f"{chave}_unalvo")
        alvo = converter_tempo(alvo, un, unidade)
    else:
        frase(c2, "clientes")
    return metrica, alvo


# --------------------------------------------------------------------------
# Aba 1 — Calculadora
# --------------------------------------------------------------------------
def painel_resultado(fila: Fila, un: str):
    res = fila.resultado()
    html(f'<div class="sec" style="margin-top:.2rem">Resultado — {fila.familia} <span style="font-weight:600;'
         f'color:#5E584D;font-size:1rem">({fila.nome})</span></div>')
    tickets([
        ("No sistema", fmt(res.L, 3), "clientes · L"),
        ("Na fila", fmt(res.Lq, 3), "clientes · Lq"),
        ("Tempo no sistema", fmt_tempo(res.W, un), "por cliente · W"),
        ("Tempo na fila", fmt_tempo(res.Wq, un), "por cliente · Wq"),
    ])
    html(f'<div class="nota">{interpretar(res, un)}</div>')
    html(diagrama_svg(fila, res.rho))

    html('<div class="sec">Todas as medidas</div>')
    esq, dir_ = st.columns([1.1, 1])
    with esq:
        st.markdown(md_tabela(["Medida", "Valor"], linhas_resultado(res, un)))
    with dir_:
        dist = fila.distribuicao()
        st.caption("Chance de haver n clientes no sistema — P(n)")
        st.bar_chart(pd.DataFrame({"P(n)": dist}, index=range(len(dist))), color="#D9480F",
                     x_label="clientes no sistema (n)", y_label="P(n)")

    html('<div class="sec">Perguntas de probabilidade</div>')
    c1, c2, c3 = st.columns([2.6, 1, 1.8])
    frase(c1, "Qual a chance de haver <b>exatamente</b>")
    ini("calc_n", 3)
    n = c2.number_input("n", min_value=0, step=1, key="calc_n", label_visibility="collapsed")
    c3.markdown(f'<div class="resp">{fmt_pct(fila.P(int(n)))}<small>clientes no sistema</small></div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2.6, 1, 1.8])
    frase(c1, "Qual a chance de haver <b>mais de</b>")
    ini("calc_r", 5)
    r = c2.number_input("r", min_value=0, step=1, key="calc_r", label_visibility="collapsed")
    c3.markdown(f'<div class="resp">{fmt_pct(fila.P_mais_que(int(r)))}<small>clientes no sistema</small></div>',
                unsafe_allow_html=True)
    if fila.finita:
        st.caption("A chance de esperar mais que um tempo t só existe para M/M/1 e M/M/s "
                   "(sem limite de capacidade e população infinita).")
        return
    for rotulo, chave, funcao in (("esperar <b>mais de</b>", "calc_tq", fila.P_Wq_maior),
                                  ("ficar no sistema <b>mais de</b>", "calc_tw", fila.P_W_maior)):
        c1, c2, c3, c4 = st.columns([2.6, 1, 1.2, 1.5])
        frase(c1, f"Qual a chance de um cliente {rotulo}")
        ini(chave, 1.0)
        ini(chave + "_un", un)
        t = c2.number_input("t", min_value=0.0, step=0.1, format="%g", key=chave, label_visibility="collapsed")
        ut = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=chave + "_un",
                          label_visibility="collapsed")
        p = funcao(converter_tempo(t, ut, un))
        c4.markdown(f'<div class="resp">{fmt_pct(p)}</div>', unsafe_allow_html=True)


def aba_calculadora():
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        p = formulario("calc", com_exemplos=True)
    with dir_:
        if p is None:
            vazio("Preencha os valores ao lado para ver o resultado.")
            return
        fila = construir_fila(p)
        if fila is not None:
            painel_resultado(fila, p["unidade"])


# --------------------------------------------------------------------------
# Aba 2 — Dimensionar
# --------------------------------------------------------------------------
def dimensionar_comparar():
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        p = formulario("cmp", variar_s=True)
        passo(4, "Custos (opcional)", "Preencha para descobrir qual número de atendentes sai mais barato.")
        un = p["unidade"] if p else "hora"
        s_max = int(st.number_input("Testar de 1 até quantos atendentes?", min_value=1, max_value=100,
                                    value=6, step=1))
        cs = st.number_input(f"Custo de manter 1 atendente (por {un})", min_value=0.0, value=0.0, step=1.0,
                             format="%g")
        cw = st.number_input(f"Custo de 1 cliente esperando (por {un})", min_value=0.0, value=0.0, step=1.0,
                             format="%g")
        espera_em = st.radio("O cliente gera custo…", ["L", "Lq"],
                             format_func=lambda x: "enquanto está no sistema (L)" if x == "L"
                             else "só enquanto espera na fila (Lq)")
        cb = st.number_input("Custo de cada cliente perdido", min_value=0.0, value=0.0, step=1.0,
                             format="%g") if (p and p["K"]) else 0.0
    with dir_:
        if p is None:
            vazio("Preencha os valores ao lado.")
            return
        try:
            resultados = comparar_servidores(p["lam"], p["mu"], 1, s_max, p["K"], p["N"])
        except ValueError as e:
            aviso(str(e))
            return
        if not resultados:
            aviso("Nenhum número de atendentes testado deixa o sistema estável. Aumente o limite de teste.")
            return
        com_custo = cs > 0 or cw > 0 or cb > 0
        custos = [custo_total(r, cs, cw, espera_em, cb) for r in resultados] if com_custo else None
        melhor = custos.index(min(custos)) if com_custo else None
        html('<div class="sec" style="margin-top:.2rem">Comparação</div>')
        if com_custo:
            html(f'<div class="nota">Menor custo com <b>{resultados[melhor].fila.s} atendente(s)</b>: '
                 f'{fmt(custos[melhor], 2)} por {un}.</div>')
        cab = ["Atendentes", "Ocupação", "L", "Lq", "W", "Wq"] + (["Custo/" + un] if com_custo else [])
        linhas = []
        for i, r in enumerate(resultados):
            l = [r.fila.s, fmt_pct(r.rho, 1), fmt(r.L, 3), fmt(r.Lq, 3), fmt_tempo(r.W, un), fmt_tempo(r.Wq, un)]
            if com_custo:
                l.append(f"<b>{fmt(custos[i], 2)} ← menor</b>" if i == melhor else fmt(custos[i], 2))
            linhas.append(l)
        st.markdown(md_tabela(cab, linhas), unsafe_allow_html=True)
        if com_custo:
            st.bar_chart(pd.DataFrame({"Custo": custos}, index=[r.fila.s for r in resultados]),
                         color="#D9480F", x_label="nº de atendentes", y_label=f"custo por {un}")
        else:
            st.caption("Preencha os custos ao lado para ver qual número de atendentes sai mais barato.")


def dimensionar_lambda():
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        p = formulario("lam", pedir_lam=False)
        metrica, alvo = passo_meta("lam", 3, p["unidade"] if p else "hora")
    with dir_:
        if p is None:
            vazio("Preencha os valores ao lado.")
            return
        un = p["unidade"]
        try:
            qualquer = p["mu"] * p["s"] / 2 if not (p["K"] or p["N"]) else p["mu"]
            lam = lambda_para_meta(Fila(qualquer, p["mu"], p["s"], p["K"], p["N"]), metrica, alvo)
        except ValueError as e:
            aviso(str(e))
            return
        conf = getattr(Fila(lam, p["mu"], p["s"], p["K"], p["N"]).resultado(), metrica)
        html('<div class="sec" style="margin-top:.2rem">Resposta</div>')
        tickets([("λ máximo", num(lam), f"clientes por {un}"),
                 ("1 chegada a cada", fmt_tempo(1 / lam, un), "tempo médio")])
        st.caption("Conferência: com esse λ, a medida escolhida vale "
                   + (fmt_tempo(conf, un) if metrica in ("W", "Wq") else fmt(conf, 4)) + ".")


def dimensionar_servidores():
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        p = formulario("srv", variar_s=True)
        metrica, alvo = passo_meta("srv", 4, p["unidade"] if p else "hora")
    with dir_:
        if p is None:
            vazio("Preencha os valores ao lado.")
            return
        s = menor_s_para_meta(p["lam"], p["mu"], metrica, alvo, p["K"], p["N"])
        if s is None:
            aviso("Nenhum número de atendentes (até 200) atinge essa meta.")
            return
        res = Fila(p["lam"], p["mu"], s, p["K"], p["N"]).resultado()
        html('<div class="sec" style="margin-top:.2rem">Resposta</div>')
        html(f'<div class="nota">Você precisa de, no mínimo, <b>{s} atendente(s)</b>.</div>')
        st.markdown(md_tabela(["Medida", "Valor"], linhas_resultado(res, p["unidade"])))


def aba_dimensionar():
    ferramenta = st.radio("O que você quer descobrir?",
                          ["Comparar nº de atendentes (e custos)", "Qual λ atinge uma meta?",
                           "Quantos atendentes preciso?"], horizontal=True)
    {"Comparar nº de atendentes (e custos)": dimensionar_comparar,
     "Qual λ atinge uma meta?": dimensionar_lambda,
     "Quantos atendentes preciso?": dimensionar_servidores}[ferramenta]()


# --------------------------------------------------------------------------
# Aba 3 — Exercícios do PDF
# --------------------------------------------------------------------------
def aba_exercicios():
    st.markdown("Os exercícios M/M do PDF, resolvidos com o mesmo motor da calculadora. "
                "A coluna **Slide** confere com o gabarito quando o PDF o traz. "
                "Para testar, abra a aba Calculadora e use *Comece por um exemplo*.")
    for i, ex in enumerate(exercicios_do_pdf()):
        with st.expander(ex.titulo, expanded=(i == 1)):
            st.write(ex.enunciado)
            st.caption("Dados: " + "  •  ".join(f"{k} = {v}" for k, v in ex.dados.items()))
            linhas = []
            for it in ex.itens:
                marca = {True: "✔ ", False: "✘ ", None: ""}[it.confere]
                linhas.append([it.letra, it.pergunta, f"**{it.resposta}**", it.formula,
                               f"{marca}{it.gabarito}" if it.gabarito else "—"])
            st.markdown(md_tabela(["Item", "O que se pede", "Resposta", "Fórmula", "Slide"], linhas))
            for it in ex.itens:
                if it.tabela:
                    st.markdown(f"**Item {it.letra}**")
                    st.markdown(md_tabela(it.cabecalho, it.tabela))
            if ex.observacao:
                st.caption(ex.observacao)


# --------------------------------------------------------------------------
# Aba 4 — Ferramentas
# --------------------------------------------------------------------------
def tabela_equivalencias(taxa: float, base: str):
    linhas = [[f"por {u}", fmt(converter_taxa(taxa, base, u), 4)] for u in UNIDADES]
    st.markdown(md_tabela(["Taxa equivalente", "clientes"], linhas))
    st.caption(f"Tempo médio entre eventos: {fmt_tempo(1 / taxa, base)}.")


def ferramenta_taxas():
    st.caption("Transforma o que você observou em λ ou μ (a mesma conta serve para as duas).")
    metodo = st.selectbox("O que você tem?", [
        "Número de clientes em um intervalo (ex.: 6 clientes em 5 min)",
        "Tempo médio entre chegadas ou de atendimento (ex.: 40 s por cliente)",
        "Lista de contagens por período (ex.: motores danificados por mês)"])
    if metodo.startswith("Número"):
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Clientes", min_value=0.0, value=6.0, step=1.0, format="%g")
        t = c2.number_input("em um intervalo de", min_value=0.0, value=5.0, step=1.0, format="%g")
        u = c3.selectbox("unidade", list(UNIDADES), index=1, format_func=lambda x: PLURAL[x])
        if t > 0 and n > 0:
            html(f'<div class="nota">Taxa = <b>{fmt(taxa_por_contagem(n, t))} clientes por {u}</b></div>')
            tabela_equivalencias(taxa_por_contagem(n, t), u)
    elif metodo.startswith("Tempo"):
        c1, c2 = st.columns(2)
        t = c1.number_input("Tempo médio por cliente", min_value=0.0, value=40.0, step=1.0, format="%g")
        u = c2.selectbox("unidade", list(UNIDADES), index=0, format_func=lambda x: PLURAL[x])
        if t > 0:
            html(f'<div class="nota">Taxa = <b>{fmt(taxa_por_tempo_medio(t))} clientes por {u}</b></div>')
            tabela_equivalencias(taxa_por_tempo_medio(t), u)
    else:
        texto = st.text_area("Contagens (separe por espaço, vírgula ou linha)",
                             "9 8 11 10 8 11 13 13 12 12 9 12 11 13 10 13 10 12 11 12 11 12 11 13 9 11 13 10 10 10")
        try:
            valores = [float(x) for x in texto.replace(",", " ").split()]
            u = st.selectbox("Período de cada contagem", list(UNIDADES), index=4, format_func=lambda x: PLURAL[x])
            taxa = taxa_por_amostra(valores)
            html(f'<div class="nota">{len(valores)} períodos, total {fmt(sum(valores), 0)} → '
                 f'taxa média = <b>{fmt(taxa)} por {u}</b></div>')
            tabela_equivalencias(taxa, u)
        except ValueError:
            aviso("Digite apenas números.")


def ferramenta_kendall():
    st.caption("Decodifica a notação A/B/m/C/K/N e diz se este projeto resolve o modelo.")
    exemplos = ["(digitar abaixo)", "M/M/3/FCFS/10/100", "D/D/3/FIFO/10/50", "G/Ep/15/SIRO/7/150",
                "M/M/70/FIFO/∞/∞", "Ep/D/1/LIFO/10/500"]
    escolha = st.selectbox("Exemplos dos slides", exemplos)
    texto = st.text_input("Notação de Kendall", "M/M/2/FCFS/10")
    notacao = texto if escolha == exemplos[0] else escolha
    try:
        k = decodificar(notacao)
    except ValueError as e:
        aviso(str(e))
        return
    st.markdown("\n".join(f"- {l}" for l in k.explicar()))
    params, msg = k.modelo_do_projeto()
    (lambda t: html(f'<div class="nota">{t}</div>') if params else aviso(t))(
        msg + ("  Use a aba Calculadora." if params else ""))


def aba_ferramentas():
    ferramenta = st.radio("Ferramenta", ["Calcular λ e μ a partir de dados", "Decodificar notação de Kendall"],
                          horizontal=True)
    (ferramenta_taxas if ferramenta.startswith("Calcular") else ferramenta_kendall)()


# --------------------------------------------------------------------------
# Página
# --------------------------------------------------------------------------
html('<div class="topo"><div class="olho">Otimização II · Teoria das Filas</div>'
     '<div class="titulo">Calculadora de filas M/M</div>'
     '<div class="sub">M/M/1 · M/M/s · M/M/1/K · M/M/s/K · M/M/1/N · M/M/s/N — '
     'preencha a ficha à esquerda, o resultado aparece à direita.</div></div>')

t1, t2, t3, t4 = st.tabs(["Calculadora", "Dimensionar", "Exercícios do PDF", "Ferramentas"])
with t1:
    aba_calculadora()
with t2:
    aba_dimensionar()
with t3:
    aba_exercicios()
with t4:
    aba_ferramentas()

with st.expander("Glossário rápido"):
    st.markdown(
        "- **λ (lambda)**: taxa de chegada — clientes que chegam por unidade de tempo.\n"
        "- **μ (mi)**: taxa de atendimento de um atendente — clientes atendidos por unidade de tempo.\n"
        "- **s**: número de atendentes (canais) em paralelo.\n"
        "- **ρ (rô)**: taxa de ocupação — fração do tempo em que cada atendente está ocupado.\n"
        "- **L / Lq**: nº médio de clientes no sistema / na fila.  **W / Wq**: tempo médio no sistema / na fila.\n"
        "- **K**: máximo de clientes que o sistema comporta (atendimento + fila). **N**: tamanho da população.\n"
        "- **Estável**: λ < s·μ. Se não for, a fila cresce sem parar e não há resultado.")
