"""
Filas M/M — interface web.   Para abrir:   streamlit run app.py

Organização da tela: à ESQUERDA a "ficha" (o que você preenche, em passos numerados,
escrita como o enunciado); à DIREITA o resultado, que muda enquanto você digita.
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd
import streamlit as st

from filas import Fila, FilaInstavel, comparar_servidores, custo_total
from filas.inverso import (MEDIDAS, avaliar, MEDIDAS_CONHECIDAS, TAXAS, TEMPOS, menor_s_criterios,
                           parametro_para_meta, resolver_por_medidas)
from filas.kendall import decodificar
from filas.mg1 import FilaMG1
from filas.poisson import media_no_intervalo
from filas.poisson import probabilidade as prob_poisson
from filas.prioridades import ClasseMG1, PrioridadesMG1, PrioridadesMMs, lams_de_percentuais
from filas.relacoes import relacoes_de_little
from filas.relatorio import interpretar, linhas_resultado
from filas.teoria import COMO_LER, GLOSSARIO, KENDALL, RELACOES
from filas.teoria import MODELOS as TEORIA_MODELOS
from filas.unidades import (ABREV, PLURAL, UNIDADES, converter_taxa, converter_tempo, fmt, fmt_pct,
                            fmt_tempo, taxa_por_amostra, taxa_por_contagem, taxa_por_tabela,
                            taxa_por_tempo_medio)

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
.ticket .val{font:600 23px/1.2 'IBM Plex Mono',monospace;color:var(--tinta);margin:4px 0 2px;white-space:nowrap}
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
LIMITES = {
    "livre": "Sem limite — a fila pode crescer à vontade",
    "K": "Limite de K clientes — se estiver cheio, quem chega vai embora",
    "N": "Só existem N clientes no total (população finita)",
}

# textos das duas formas de dar o dado (o enunciado diz uma ou outra)
TXT_CHEGADA = {
    "tempo": dict(exemplo="“chega 1 cliente a cada 12 min”", antes="Chega 1 cliente a cada"),
    "taxa": dict(exemplo="“chegam 5 clientes por hora”", antes="Chegam", meio="clientes por"),
}
TXT_CHEGADA_N = {
    "tempo": dict(exemplo="“cada cliente volta a cada 6 h”", antes="Cada cliente fora do sistema volta a cada"),
    "taxa": dict(exemplo="“cada cliente volta 0,2 vez por hora”", antes="Cada cliente volta", meio="vez(es) por"),
}
TXT_ATEND = {
    "tempo": dict(exemplo="“cada atendimento leva 8 min”", antes="Cada atendimento leva"),
    "taxa": dict(exemplo="“cada atendente atende 7 clientes por hora”", antes="Cada atendente atende",
                 meio="clientes por"),
}
# (dica no campo vazio, unidade inicial)
PAD_CHEGADA = {"tempo": ("ex.: 12", "minuto"), "taxa": ("ex.: 5", "hora")}
PAD_CHEGADA_N = {"tempo": ("ex.: 6", "hora"), "taxa": ("ex.: 0,2", "hora")}
PAD_ATEND = {"tempo": ("ex.: 8", "minuto"), "taxa": ("ex.: 7", "hora")}

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
# A ficha: passos numerados, escritos como o enunciado
# --------------------------------------------------------------------------
def cartao_taxa(chave: str, numero: int, titulo: str, ajuda: str, textos: dict, padroes: dict,
                simbolo: str):
    """Um campo escrito como frase do enunciado. Devolve a taxa por SEGUNDO (ou None)."""
    passo(numero, titulo, ajuda)
    modo = st.radio("O enunciado diz…", ["tempo", "taxa"], key=f"{chave}_modo",
                    format_func=lambda m: textos[m]["exemplo"])
    t = textos[modo]
    dica, un0 = padroes[modo]
    k_val, k_un = f"{chave}_valor_{modo}", f"{chave}_un_{modo}"
    ini(k_un, un0)
    if modo == "tempo":
        c1, c2, c3 = st.columns([3.4, 1.3, 1.7])
        frase(c1, t["antes"])
        valor = c2.number_input("valor", min_value=0.0, value=None, placeholder=dica, step=1.0,
                                format="%g", key=k_val, label_visibility="collapsed")
        unid = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=k_un,
                            label_visibility="collapsed")
    else:
        c1, c2, c3, c4 = st.columns([2.3, 1.2, 1.7, 1.5])
        frase(c1, t["antes"])
        valor = c2.number_input("valor", min_value=0.0, value=None, placeholder=dica, step=0.1,
                                format="%g", key=k_val, label_visibility="collapsed")
        frase(c3, t["meio"])
        unid = c4.selectbox("unidade", list(UNIDADES), key=k_un, label_visibility="collapsed")
    if valor is None or valor <= 0:
        html('<div class="eco">Informe um valor maior que zero para continuar.</div>')
        return None
    taxa_s = (taxa_por_tempo_medio(converter_tempo(valor, unid, "segundo")) if modo == "tempo"
              else converter_taxa(valor, unid, "segundo"))
    html(f'<div class="eco">{simbolo} = {num(taxa_s * 3600)} por hora &nbsp;·&nbsp; '
         f'1 a cada {fmt_tempo(1 / taxa_s, "segundo")}</div>')
    return taxa_s


def cartao_medidas(chave: str, numero: int, s: int):
    """Duas medidas conhecidas -> (λ, μ) por segundo. Para enunciados que não dão λ e μ diretamente."""
    passo(numero, "Quais medidas o enunciado dá?",
          "Escolha duas (ex.: ρ e Wq, ou Lq e W, ou λ e ρ). O programa descobre λ e μ.")
    conhecidos = []
    for i, padrao in enumerate(("rho", "Wq")):
        ini(f"{chave}_mc{i}_tipo", padrao)
        c1, c2, c3 = st.columns([2.8, 1.3, 1.6])
        tipo = c1.selectbox(f"Medida {i + 1}", list(MEDIDAS_CONHECIDAS), format_func=MEDIDAS_CONHECIDAS.get,
                            key=f"{chave}_mc{i}_tipo", label_visibility="collapsed")
        valor = c2.number_input("valor", min_value=0.0, value=None, placeholder="valor", format="%g",
                                key=f"{chave}_mc{i}_valor_{tipo}", label_visibility="collapsed")
        if tipo in TEMPOS:
            ini(f"{chave}_mc{i}_un_t", "minuto")
            unid = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u],
                                key=f"{chave}_mc{i}_un_t", label_visibility="collapsed")
        elif tipo in TAXAS:
            ini(f"{chave}_mc{i}_un_r", "hora")
            unid = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: f"por {u}",
                                key=f"{chave}_mc{i}_un_r", label_visibility="collapsed")
        else:
            unid = None
            frase(c3, "fração ou %" if tipo in ("rho", "P0") else "clientes")
        if valor is None or valor <= 0:
            html('<div class="eco">Informe as duas medidas para continuar.</div>')
            return None
        if tipo in ("rho", "P0") and valor > 1:
            valor = valor / 100                      # aceita 75 como 75%
        if tipo in TEMPOS:
            valor = converter_tempo(valor, unid, "segundo")
        elif tipo in TAXAS:
            valor = converter_taxa(valor, unid, "segundo")
        conhecidos.append((tipo, valor))
    try:
        solucoes = resolver_por_medidas(int(s), conhecidos)
    except ValueError as e:                         # inclui FilaInstavel
        aviso(f"<b>Não dá para calcular:</b> {e}")
        return None
    lam_s, mu_s = solucoes[0]
    mais = " (há mais de uma solução; usando a primeira)" if len(solucoes) > 1 else ""
    html(f'<div class="eco">λ = {num(lam_s * 3600)} por hora &nbsp;·&nbsp; μ = {num(mu_s * 3600)} por hora{mais}</div>')
    return lam_s, mu_s


def _caixa_unidade(chave: str, rotulo="Mostrar os tempos do resultado em"):
    html('<div style="height:.9rem"></div>')
    ini(f"{chave}_unidade", "hora")
    return st.selectbox(rotulo, list(UNIDADES), format_func=lambda u: PLURAL[u], key=f"{chave}_unidade")


def formulario(chave: str, variar_s: bool = False, pedir_lam: bool = True, pedir_mu: bool = True,
               permitir_medidas: bool = False):
    """
    Ficha dos modelos M/M. Devolve dict(lam, mu, s, K, N, unidade) ou None se faltar dado.
    variar_s=True      -> o nº de atendentes não é perguntado (a ferramenta testa vários).
    pedir_lam/pedir_mu -> False quando a ferramenta é que descobre esse parâmetro.
    permitir_medidas   -> deixa o enunciado dar outras medidas (ρ, Lq, W…) em vez de λ e μ.
    """
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
        modo_k = "total"
        if not variar_s:
            modo_k = st.radio("O enunciado informa…", ["total", "espera"], key=f"{chave}_Kmodo",
                              format_func={"total": "o máximo de clientes no sistema (K)",
                                           "espera": "só os lugares de espera, além dos atendentes"}.get)
        if modo_k == "total":
            K = st.number_input("K = máximo de clientes no sistema (conta quem está sendo atendido + a fila)",
                                min_value=1, value=None, placeholder="ex.: 10", step=1, key=f"{chave}_K")
        else:
            esp = st.number_input("Quantos lugares de ESPERA existem? (sem contar quem está sendo atendido)",
                                  min_value=0, value=None, placeholder="ex.: 3", step=1, key=f"{chave}_Kesp")
            if esp is not None:
                K = int(s) + int(esp)
                html(f'<div class="eco">K = {int(s)} em atendimento + {int(esp)} esperando = {K}</div>')
    elif limite == "N":
        N = st.number_input("N = quantos clientes existem no total", min_value=1, value=None,
                            placeholder="ex.: 20", step=1, key=f"{chave}_N")
    if not variar_s:
        extra = f" · K = {int(K)}" if K else (f" · N = {int(N)}" if N else "")
        html(f'<div class="modelo">Modelo: <b>{nome_modelo(int(s), limite)}</b>'
             f'&nbsp;({int(s)} atendente{"s" if s > 1 else ""}{extra})</div>')
    else:
        html(f'<div class="modelo">Modelo: <b>M/M/s{"" if limite == "livre" else "/" + limite}</b>'
             '&nbsp;(o nº de atendentes será testado)</div>')

    # ---- passos 2 e 3: taxas
    numero = 2
    usar_medidas = False
    if permitir_medidas and limite == "livre" and pedir_lam and pedir_mu:
        passo(2, "O que o enunciado informa?")
        ini(f"{chave}_dados", "taxas")
        usar_medidas = st.radio("dados", ["taxas", "medidas"], key=f"{chave}_dados", label_visibility="collapsed",
                                format_func={"taxas": "A chegada (λ) e o atendimento (μ): taxas ou tempos médios",
                                             "medidas": "Outras medidas: ρ, L, Lq, W, Wq, P0… (o programa descobre λ e μ)"}.get
                                ) == "medidas"
        numero = 3
    lam_s, mu_s = 1.0 / 3600, 1.0 / 3600
    if usar_medidas:
        achados = cartao_medidas(chave, numero, int(s))
        lam_s, mu_s = achados if achados else (None, None)
    else:
        if pedir_lam:
            if limite == "N":
                lam_s = cartao_taxa(f"{chave}_lamN", numero, "Com que frequência os clientes voltam?",
                                    "Aqui λ é de CADA cliente que está fora do sistema.", TXT_CHEGADA_N,
                                    PAD_CHEGADA_N, "λ por cliente")
            else:
                lam_s = cartao_taxa(f"{chave}_lam", numero, "Quanto chega?",
                                    "É a taxa de chegada, λ.", TXT_CHEGADA, PAD_CHEGADA, "λ")
            numero += 1
        if pedir_mu:
            mu_s = cartao_taxa(f"{chave}_mu", numero, "Quanto cada atendente atende?",
                               "É a taxa de atendimento, μ — de UM atendente.", TXT_ATEND, PAD_ATEND, "μ")

    unidade = _caixa_unidade(chave)
    if lam_s is None or mu_s is None or (limite == "K" and not K) or (limite == "N" and not N):
        return None
    return dict(lam=lam_s * UNIDADES[unidade], mu=mu_s * UNIDADES[unidade], s=int(s),
                K=int(K) if K else None, N=int(N) if N else None, unidade=unidade)


def construir_fila(p: dict):
    try:
        return Fila(p["lam"], p["mu"], p["s"], p["K"], p["N"])
    except ValueError as e:     # inclui FilaInstavel
        aviso(f"<b>Não dá para calcular:</b> {e}")
    return None


VARIABILIDADE = {
    "exp": "Exponencial (o desvio padrão é igual ao tempo médio)",
    "det": "Constante — sempre o mesmo tempo (σ = 0)",
    "erl": "Erlang com k fases",
    "sigma": "Conheço o desvio padrão σ",
}


def formulario_mg1(chave: str, pedir_lam: bool = True, pedir_mu: bool = True):
    """Ficha do M/G/1. Devolve dict(lam, mu, sigma, erlang_k, unidade) ou None."""
    passo(1, "Como é o sistema?", "Um único atendente e fila sem limite. O atendimento NÃO precisa ser exponencial.")
    numero = 2
    lam_s, mu_s = 1.0 / 3600, 1.0 / 3600
    if pedir_lam:
        lam_s = cartao_taxa(f"{chave}_lam", numero, "Quanto chega?", "É a taxa de chegada, λ.",
                            TXT_CHEGADA, PAD_CHEGADA, "λ")
        numero += 1
    if pedir_mu:
        mu_s = cartao_taxa(f"{chave}_mu", numero, "Qual o tempo médio de atendimento?",
                           "É a média 1/μ, qualquer que seja a distribuição.", TXT_ATEND, PAD_ATEND, "μ")
        numero += 1
    passo(numero, "Quanto o tempo de atendimento varia?",
          "Só a média e o desvio padrão importam. Quanto maior σ, maior a fila.")
    modo = st.radio("variabilidade", list(VARIABILIDADE), format_func=VARIABILIDADE.get, key=f"{chave}_var",
                    label_visibility="collapsed")
    erlang_k, sigma_s = None, None
    if modo == "erl":
        k = st.number_input("k = número de fases", min_value=1, value=None, placeholder="ex.: 4", step=1,
                            key=f"{chave}_k")
        if k is None:
            html('<div class="eco">Informe k para continuar.</div>')
        erlang_k = int(k) if k else None
    elif modo == "sigma":
        ini(f"{chave}_sg_un", "minuto")
        c1, c2, c3 = st.columns([3.4, 1.3, 1.7])
        frase(c1, "O desvio padrão do atendimento é")
        sg = c2.number_input("σ", min_value=0.0, value=None, placeholder="ex.: 2", step=0.5, format="%g",
                             key=f"{chave}_sg", label_visibility="collapsed")
        sg_un = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=f"{chave}_sg_un",
                             label_visibility="collapsed")
        if sg is None:
            html('<div class="eco">Informe σ (pode ser 0) para continuar.</div>')
        else:
            sigma_s = converter_tempo(sg, sg_un, "segundo")
    unidade = _caixa_unidade(chave)
    faltando = (lam_s is None or mu_s is None or (modo == "erl" and erlang_k is None)
                or (modo == "sigma" and sigma_s is None))
    if faltando:
        return None
    sigma = {"exp": None, "erl": None, "det": 0.0, "sigma": None if sigma_s is None else sigma_s / UNIDADES[unidade]}[modo]
    return dict(lam=lam_s * UNIDADES[unidade], mu=mu_s * UNIDADES[unidade], sigma=sigma, erlang_k=erlang_k,
                unidade=unidade)


def construir_mg1(p: dict):
    try:
        return FilaMG1(p["lam"], p["mu"], p["sigma"], p["erlang_k"])
    except ValueError as e:
        aviso(f"<b>Não dá para calcular:</b> {e}")
    return None


def formulario_prioridades(chave: str):
    """Ficha das filas com prioridades. Devolve dict com o necessário para montar o modelo, ou None."""
    passo(1, "Como é o sistema?", "Os clientes têm classes. A classe 1 tem a maior prioridade.")
    tipo = st.radio("Atendimento", ["mms", "mg1"], key=f"{chave}_tipo",
                    format_func={"mms": "Exponencial e igual para todas as classes (M/M/s, mesma taxa μ)",
                                 "mg1": "Cada classe com seu tempo de atendimento (1 atendente, M/G/1)"}.get)
    s, interrupcao, spt = 1, False, False
    if tipo == "mms":
        c1, c2 = st.columns(2)
        ini(f"{chave}_s", 1)
        s = c1.number_input("Atendentes", min_value=1, step=1, key=f"{chave}_s")
        interrupcao = c2.radio("Prioridade", [False, True], key=f"{chave}_int",
                               format_func=lambda x: "COM interrupção" if x else "SEM interrupção",
                               help="Com interrupção, a chegada de uma classe maior tira o atendimento da classe menor. "
                                    "Sem interrupção, o atendimento em curso termina.") is True
    else:
        spt = st.checkbox("Ordenar pelo menor tempo de atendimento (disciplina SPT)", key=f"{chave}_spt")
    ini(f"{chave}_nclasses", 2)
    n = int(st.number_input("Quantas classes?", min_value=1, max_value=8, step=1, key=f"{chave}_nclasses"))

    passo(2, "Quanto chega em cada classe?", "Informe λ de cada classe, ou λ total e a porcentagem de cada uma.")
    modo_lam = st.radio("Chegadas", ["cada", "pct"], horizontal=True, key=f"{chave}_modolam",
                        format_func={"cada": "λ de cada classe", "pct": "λ total e % de cada classe"}.get,
                        label_visibility="collapsed")
    ini(f"{chave}_un_lam", "hora")
    un_lam = st.selectbox("Chegadas por…", list(UNIDADES), format_func=lambda u: f"por {u}",
                          key=f"{chave}_un_lam")
    lams, pcts, total = [], [], None
    if modo_lam == "pct":
        total = st.number_input("λ total", min_value=0.0, value=None, placeholder="ex.: 2", step=0.1, format="%g",
                                key=f"{chave}_total")
    for i in range(n):
        c1, c2 = st.columns([1, 2])
        frase(c1, f"Classe {i + 1}")
        if modo_lam == "cada":
            lams.append(c2.number_input(f"λ da classe {i + 1}", min_value=0.0, value=None, placeholder="clientes",
                                        step=0.1, format="%g", key=f"{chave}_lam{i}", label_visibility="collapsed"))
        else:
            pcts.append(c2.number_input(f"% da classe {i + 1}", min_value=0.0, max_value=100.0, value=None,
                                        placeholder="% do total", step=1.0, format="%g", key=f"{chave}_pct{i}",
                                        label_visibility="collapsed"))
    if modo_lam == "pct" and pcts and all(p is not None for p in pcts) and abs(sum(pcts) - 100) > 1e-6:
        html(f'<div class="eco">As porcentagens somam {num(sum(pcts), 2)}% (e não 100%). '
             'O programa divide o λ total proporcionalmente a elas.</div>')
    classes_mg1, mu_s = [], None
    if tipo == "mms":
        mu_s = cartao_taxa(f"{chave}_mu", 3, "Quanto cada atendente atende?",
                           "Mesma taxa μ para todas as classes.", TXT_ATEND, PAD_ATEND, "μ")
    else:
        passo(3, "Como é o atendimento de cada classe?",
              "Tempo médio e desvio padrão. Se deixar σ vazio, o atendimento é exponencial (σ = média).")
        ini(f"{chave}_un_es", "minuto")
        un_es = st.selectbox("Tempos de atendimento em…", list(UNIDADES), format_func=lambda u: PLURAL[u],
                             key=f"{chave}_un_es")
        for i in range(n):
            c1, c2, c3 = st.columns([1, 1.6, 1.6])
            frase(c1, f"Classe {i + 1}")
            es = c2.number_input(f"tempo médio da classe {i + 1}", min_value=0.0, value=None, placeholder="média",
                                 step=0.5, format="%g", key=f"{chave}_es{i}", label_visibility="collapsed")
            sg = c3.number_input(f"σ da classe {i + 1}", min_value=0.0, value=None, placeholder="σ (opcional)",
                                 step=0.5, format="%g", key=f"{chave}_sg{i}", label_visibility="collapsed")
            classes_mg1.append((es, sg))
    unidade = _caixa_unidade(chave)

    # ---- consolida em unidade base
    if modo_lam == "pct":
        if total is None or total <= 0 or any(p is None for p in pcts) or sum(pcts) <= 0:
            return None
        lams_s = [l / UNIDADES["segundo"] for l in lams_de_percentuais(converter_taxa(total, un_lam, "segundo"), pcts)]
    else:
        if any(l is None or l <= 0 for l in lams):
            return None
        lams_s = [converter_taxa(l, un_lam, "segundo") for l in lams]
    f = UNIDADES[unidade]
    lams_b = [l * f for l in lams_s]
    if tipo == "mms":
        if mu_s is None:
            return None
        return dict(tipo=tipo, lams=lams_b, mu=mu_s * f, s=int(s), interrupcao=interrupcao, unidade=unidade)
    if any(es is None or es <= 0 for es, _ in classes_mg1):
        return None
    cls = [ClasseMG1(l, converter_tempo(es, un_es, unidade),
                     None if sg is None else converter_tempo(sg, un_es, unidade))
           for l, (es, sg) in zip(lams_b, classes_mg1)]
    return dict(tipo=tipo, classes=cls, spt=spt, unidade=unidade)


# --------------------------------------------------------------------------
# Painéis de resultado
# --------------------------------------------------------------------------
ID_TEORIA = {"M/M/1": "mm1", "M/M/s": "mms", "M/M/1/K": "mm1k", "M/M/s/K": "mmsk", "M/M/1/N": "mm1n",
             "M/M/s/N": "mmsn", "M/G/1": "mg1", "Prioridades": "prio"}


def mostrar_formulas(familia: str):
    """Expander com as fórmulas do modelo (as mesmas da aba Teoria)."""
    modelo = next(m for m in TEORIA_MODELOS if m["id"] == ID_TEORIA[familia])
    with st.expander(f"Fórmulas do modelo {familia}"):
        st.caption(modelo["quando"])
        for rotulo, tex in modelo["formulas"]:
            if rotulo:
                st.markdown(f"**{rotulo}**")
            st.latex(tex)
        st.caption(modelo["dica"])


def painel_resultado(fila, un: str):
    """Painel para Fila (M/M) e FilaMG1."""
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
    mg1 = isinstance(fila, FilaMG1)
    if mg1:
        st.markdown(md_tabela(["Medida", "Valor"], linhas_resultado(res, un)))
    else:
        esq, dir_ = st.columns([1.1, 1])
        with esq:
            st.markdown(md_tabela(["Medida", "Valor"], linhas_resultado(res, un)))
        with dir_:
            dist = fila.distribuicao()
            st.caption("Chance de haver n clientes no sistema — P(n)")
            st.bar_chart(pd.DataFrame({"P(n)": dist}, index=range(len(dist))), color="#D9480F",
                         x_label="clientes no sistema (n)", y_label="P(n)")
        with st.expander("Ver tabela de P(n)"):
            acum, linhas = 0.0, []
            for k, pk in enumerate(dist):
                acum += pk
                linhas.append([k, fmt(pk, 6), fmt(min(acum, 1.0), 6)])
            st.markdown(md_tabela(["n", "P(n = k)", "P(n ≤ k)"], linhas))
    mostrar_formulas(fila.familia)
    if mg1:
        painel_variar_sigma(fila, un)
    else:
        painel_consultas(fila, un)


def painel_variar_sigma(fila: FilaMG1, un: str):
    html('<div class="sec">E se a variabilidade mudar?</div>')
    st.caption("Veja como as medidas mudam variando o desvio padrão σ do atendimento (a média 1/μ fica igual). "
               "Informe os valores separados por vírgula, na unidade escolhida.")
    c1, c2 = st.columns([3, 1.4])
    texto = c1.text_input("Valores de σ", placeholder="ex.: 4, 3, 2, 1, 0", key="mg_sigmas")
    ini("mg_sigmas_un", "minuto")
    unid = c2.selectbox("unidade de σ", list(UNIDADES), format_func=lambda u: PLURAL[u], key="mg_sigmas_un")
    if not texto.strip():
        return
    try:
        valores = [float(x) for x in texto.replace(",", " ").replace(";", " ").split()]
        if any(v < 0 for v in valores):
            raise ValueError("σ não pode ser negativo.")
    except ValueError as e:
        aviso(f"Digite números separados por vírgula. {e}")
        return
    linhas, lq_ant, lq_ref = [], None, None
    for v in valores:
        r = FilaMG1(fila.lam, fila.mu, converter_tempo(v, unid, un)).resultado()
        lq_ref = r.Lq if lq_ref is None else lq_ref
        reducao = "—" if lq_ant is None else fmt(lq_ant - r.Lq, 4)
        linhas.append([fmt(v, 2).rstrip("0").rstrip(","), fmt(r.Lq, 4), fmt(r.L, 4), fmt_tempo(r.Wq, un), fmt_tempo(r.W, un),
                       reducao, fmt(r.Lq / lq_ref, 3)])
        lq_ant = r.Lq
    st.markdown(md_tabela(["σ", "Lq", "L", "Wq", "W", "Redução de Lq", "Lq ÷ Lq do 1º"], linhas))


# ---- consultas gerais (M/M) --------------------------------------------
VARS = {
    "n": "Clientes no sistema (n)",
    "nq": "Clientes na fila (nq)",
    "W": "Tempo no sistema (W)",
    "Wq": "Tempo na fila (Wq)",
    "pW": "Percentil de W",
    "pWq": "Percentil de Wq",
}
OPS_N = ["=", "<", "≤", ">", "≥", "entre"]


def _consulta(fila: Fila, un: str, i: int):
    c1, c2, c3, c4, c5 = st.columns([2.6, 1.2, 1.2, 1.5, 1.6])
    var = c1.selectbox("Pergunta", list(VARS), format_func=VARS.get, key=f"q{i}_var",
                       label_visibility="collapsed")
    resultado, extra = "—", ""
    try:
        if var in ("n", "nq"):
            op = c2.selectbox("op", OPS_N, key=f"q{i}_{var}_op", label_visibility="collapsed")
            a = c3.number_input("a", min_value=0, value=None, placeholder="valor", step=1,
                                key=f"q{i}_{var}_a", label_visibility="collapsed")
            b = None
            if op == "entre":
                b = c4.number_input("b", min_value=0, value=None, placeholder="até", step=1,
                                    key=f"q{i}_{var}_b", label_visibility="collapsed")
            if a is not None and (op != "entre" or b is not None):
                f = fila.P_fila if var == "nq" else fila.P_clientes
                resultado = fmt_pct(f(op, int(a), None if b is None else int(b)))
        elif var in ("W", "Wq"):
            ops = [">", "≤"] + (["= 0 (não espera)"] if var == "Wq" else [])
            op = c2.selectbox("op", ops, key=f"q{i}_{var}_op", label_visibility="collapsed")
            if op.startswith("="):
                resultado = fmt_pct(1 - fila.P_Wq_maior(0.0))
            else:
                ini(f"q{i}_{var}_un", "minuto")
                t = c3.number_input("t", min_value=0.0, value=None, placeholder="tempo", step=0.1,
                                    format="%g", key=f"q{i}_{var}_t", label_visibility="collapsed")
                ut = c4.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u],
                                  key=f"q{i}_{var}_un", label_visibility="collapsed")
                if t is not None:
                    cauda = (fila.P_Wq_maior if var == "Wq" else fila.P_W_maior)(converter_tempo(t, ut, un))
                    resultado = fmt_pct(cauda if op == ">" else 1 - cauda)
        else:  # percentis
            c2.markdown('<div class="frase">em</div>', unsafe_allow_html=True)
            pct = c3.number_input("percentual", min_value=0.0, max_value=99.99, value=None, placeholder="ex.: 95",
                                  step=1.0, format="%g", key=f"q{i}_{var}_p", label_visibility="collapsed")
            c4.markdown('<div class="frase">% dos casos, até…</div>', unsafe_allow_html=True)
            if pct:
                t = fila.tempo_percentil(pct / 100, "W" if var == "pW" else "Wq")
                resultado = fmt_tempo(t, un)
    except ValueError as e:
        resultado, extra = "—", str(e)
    c5.markdown(f'<div class="resp">{resultado}</div>', unsafe_allow_html=True)
    if extra:
        st.caption(extra)


def painel_consultas(fila: Fila, un: str):
    html('<div class="sec">Consultas de probabilidade</div>')
    st.caption("Monte qualquer pergunta: escolha a variável, a comparação e o valor. "
               "Adicione quantas consultas quiser.")
    ini("calc_nconsultas", 2)
    for i in range(st.session_state["calc_nconsultas"]):
        _consulta(fila, un, i)
    c1, c2, _ = st.columns([2, 2, 3])
    if c1.button("+ Adicionar consulta", key="calc_mais"):
        st.session_state["calc_nconsultas"] += 1
        st.rerun()
    if c2.button("− Remover última", key="calc_menos", disabled=st.session_state["calc_nconsultas"] <= 1):
        st.session_state["calc_nconsultas"] -= 1
        st.rerun()


def painel_prioridades(modelo, un: str):
    """modelo: PrioridadesMMs ou PrioridadesMG1."""
    r = modelo.resultado()
    html(f'<div class="sec" style="margin-top:.2rem">Resultado — prioridades {r.disciplina}</div>')
    if isinstance(modelo, PrioridadesMMs):
        lams_txt = " · ".join(f"λ{c.classe} = {num(c.lam)}" for c in r.classes)
        usados = (f"{lams_txt} (total {num(sum(modelo.lams))} por {un}) · μ = {num(modelo.mu)} por {un} "
                  f"em cada atendente · {modelo.s} atendente(s) · ocupação ρ = "
                  f"{fmt_pct(sum(modelo.lams) / (modelo.s * modelo.mu), 1)}")
    else:
        partes = [f"classe {c.classe}: λ = {num(c.lam)}, atendimento médio {fmt_tempo(modelo.classes[c.classe - 1].media, un)}"
                  for c in r.classes]
        usados = (" · ".join(partes) + f" · ocupação ρ = "
                  f"{fmt_pct(sum(k.lam * k.media for k in modelo.classes), 1)}")
    html(f'<div class="eco" style="margin:.2rem 0 .8rem"><b>Dados usados no cálculo (λ por {un}):</b> {usados}</div>')
    linhas = []
    for c in r.classes:
        linhas.append([f"Classe {c.classe}", c.prioridade, num(c.lam), fmt(c.L, 4), fmt(c.Lq, 4),
                       fmt_tempo(c.W, un), fmt_tempo(c.Wq, un)])
    g = r.geral
    linhas.append(["<b>Todos (média, igual à FIFO)</b>", "—", num(g.lam), fmt(g.L, 4), fmt(g.Lq, 4),
                   fmt_tempo(g.W, un), fmt_tempo(g.Wq, un)])
    st.markdown(md_tabela(["Classe", "Prioridade", f"λ (por {un})", "L", "Lq", "W", "Wq"], linhas),
                unsafe_allow_html=True)
    frases = [f"A <b>classe {c.classe}</b> espera {fmt_tempo(c.Wq, un)} na fila e fica {fmt_tempo(c.W, un)} no sistema."
              for c in r.classes]
    html('<div class="nota">' + "<br>".join(frases) + "</div>")
    if isinstance(modelo, PrioridadesMMs):
        html('<div class="sec">Comparar as disciplinas</div>')
        st.caption("Tempo médio no sistema (W) de cada classe em cada disciplina de atendimento.")
        sem = PrioridadesMMs(modelo.lams, modelo.mu, modelo.s, False).resultado()
        com = PrioridadesMMs(modelo.lams, modelo.mu, modelo.s, True).resultado()
        comp = [[f"Classe {i + 1}", fmt_tempo(sem.geral.W, un), fmt_tempo(sem.classes[i].W, un),
                 fmt_tempo(com.classes[i].W, un)] for i in range(len(modelo.lams))]
        st.markdown(md_tabela(["", "FIFO (sem prioridade)", "Prioridade sem interrupção",
                               "Prioridade com interrupção"], comp))
    mostrar_formulas("Prioridades")


def aba_calculadora():
    tipo = st.radio("Tipo de sistema", ["mm", "mg1", "prio"], horizontal=True, key="calc_tipo",
                    format_func={"mm": "Filas M/M (atendimento exponencial)",
                                 "mg1": "M/G/1 (atendimento qualquer)",
                                 "prio": "Com prioridades"}.get)
    esq, dir_ = st.columns([5, 6], gap="large")
    if tipo == "mm":
        with esq:
            p = formulario("calc", permitir_medidas=True)
        with dir_:
            if p is None:
                vazio("Responda aos passos ao lado.<br>O resultado aparece aqui, completo, "
                      "para qualquer modelo M/M.")
            else:
                fila = construir_fila(p)
                if fila is not None:
                    painel_resultado(fila, p["unidade"])
    elif tipo == "mg1":
        with esq:
            p = formulario_mg1("mg")
        with dir_:
            if p is None:
                vazio("Responda aos passos ao lado.<br>O M/G/1 usa a fórmula de Pollaczek-Khintchine.")
            else:
                fila = construir_mg1(p)
                if fila is not None:
                    painel_resultado(fila, p["unidade"])
    else:
        with esq:
            p = formulario_prioridades("pr")
        with dir_:
            if p is None:
                vazio("Responda aos passos ao lado.<br>Informe λ de cada classe e o atendimento.")
            else:
                try:
                    modelo = (PrioridadesMMs(p["lams"], p["mu"], p["s"], p["interrupcao"]) if p["tipo"] == "mms"
                              else PrioridadesMG1(p["classes"], p["spt"]))
                    painel_prioridades(modelo, p["unidade"])
                except ValueError as e:
                    aviso(f"<b>Não dá para calcular:</b> {e}")


# --------------------------------------------------------------------------
# Aba Dimensionar
# --------------------------------------------------------------------------
TIPOS_MM = list(MEDIDAS)
TIPOS_MG1 = ["L", "Lq", "W", "Wq", "rho", "P0"]


def seletor_medida(chave: str, tipos: list, unidade: str, rotulo: str = "Medida"):
    """Escolha de uma medida (com o argumento r ou t, se precisar). Devolve (tipo, arg na unidade base)."""
    ini(f"{chave}_tipo", tipos[0])
    c1, c2, c3 = st.columns([2.7, 1.2, 1.5])
    tipo = c1.selectbox(rotulo, tipos, format_func=lambda t: MEDIDAS[t][0], key=f"{chave}_tipo")
    kind, arg = MEDIDAS[tipo][1], None
    if kind == "int":
        r = c2.number_input("r", min_value=0, value=None, placeholder="r", step=1, key=f"{chave}_arg{tipo}",
                            label_visibility="collapsed")
        arg = None if r is None else int(r)
    elif kind == "tempo":
        ini(f"{chave}_argun", "minuto")
        t = c2.number_input("t", min_value=0.0, value=None, placeholder="t", step=0.1, format="%g",
                            key=f"{chave}_arg{tipo}", label_visibility="collapsed")
        ut = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=f"{chave}_argun",
                          label_visibility="collapsed")
        arg = None if t is None else converter_tempo(t, ut, unidade)
    return tipo, arg


def valor_da_medida(chave: str, tipo: str, unidade: str, rotulo: str = "Valor"):
    """Valor-alvo de uma medida, em unidade base (probabilidades em fração). None se faltar."""
    if tipo in ("W", "Wq"):
        c1, c2 = st.columns([1, 1.5])
        ini(f"{chave}_valun", unidade)
        v = c1.number_input(rotulo, min_value=0.0, value=None, placeholder="tempo", step=0.1, format="%g",
                            key=f"{chave}_val_t")
        un = c2.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key=f"{chave}_valun")
        return None if v is None else converter_tempo(v, un, unidade)
    if tipo in ("L", "Lq"):
        v = st.number_input(rotulo + " (clientes)", min_value=0.0, value=None, placeholder="clientes", step=0.1,
                            format="%g", key=f"{chave}_val_n")
        return v
    v = st.number_input(rotulo + " (%)", min_value=0.0, max_value=100.0, value=None, placeholder="em %", step=1.0,
                        format="%g", key=f"{chave}_val_p")
    return None if v is None else v / 100.0


def formatar_medida(tipo: str, valor: float, unidade: str) -> str:
    if tipo in ("W", "Wq"):
        return fmt_tempo(valor, unidade)
    if tipo in ("L", "Lq"):
        return fmt(valor, 4)
    return fmt_pct(valor, 2)


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
        so_ocupado = st.checkbox("O atendente só é pago enquanto está ocupado (pode ser realocado nas folgas)")
        cw = st.number_input(f"Custo de 1 cliente esperando (por {un})", min_value=0.0, value=0.0, step=1.0,
                             format="%g")
        espera_em = st.radio("O cliente gera custo…", ["L", "Lq"],
                             format_func=lambda x: "enquanto está no sistema (L)" if x == "L"
                             else "só enquanto espera na fila (Lq)")
        cb = st.number_input("Custo de cada cliente perdido", min_value=0.0, value=0.0, step=1.0,
                             format="%g") if (p and p["K"]) else 0.0
        periodo = st.number_input(f"Mostrar o custo por período de quantas unidades de tempo? "
                                  f"(ex.: um dia de 8 {PLURAL[un]})", min_value=0.0, value=1.0, step=1.0, format="%g")
    with dir_:
        if p is None:
            vazio("Responda aos passos ao lado.")
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
        custos = ([custo_total(r, cs, cw, espera_em, cb, so_ocupado) * periodo for r in resultados]
                  if com_custo else None)
        melhor = custos.index(min(custos)) if com_custo else None
        html('<div class="sec" style="margin-top:.2rem">Comparação</div>')
        if com_custo:
            html(f'<div class="nota">Menor custo com <b>{resultados[melhor].fila.s} atendente(s)</b>: '
                 f'{fmt(custos[melhor], 2)} por período.</div>')
        cab = ["Atendentes", "Ocupação", "L", "Lq", "W", "Wq"] + (["Custo/período"] if com_custo else [])
        linhas = []
        for i, r in enumerate(resultados):
            l = [r.fila.s, fmt_pct(r.rho, 1), fmt(r.L, 3), fmt(r.Lq, 3), fmt_tempo(r.W, un), fmt_tempo(r.Wq, un)]
            if com_custo:
                l.append(f"<b>{fmt(custos[i], 2)} ← menor</b>" if i == melhor else fmt(custos[i], 2))
            linhas.append(l)
        st.markdown(md_tabela(cab, linhas), unsafe_allow_html=True)
        if com_custo:
            st.bar_chart(pd.DataFrame({"Custo": custos}, index=[r.fila.s for r in resultados]),
                         color="#D9480F", x_label="nº de atendentes", y_label="custo por período")
        else:
            st.caption("Preencha os custos ao lado para ver qual número de atendentes sai mais barato.")


def dimensionar_meta():
    st.caption("Descobre a taxa de chegada (λ) ou a taxa de atendimento (μ) para que uma medida chegue ao valor desejado. "
               "Ex.: \"que taxa de atendimento faz o cliente ficar só 2 min no sistema?\"")
    modelo = st.radio("Modelo", ["mm", "mg1"], horizontal=True, key="meta_modelo",
                      format_func={"mm": "M/M (todos os modelos)", "mg1": "M/G/1"}.get)
    param = st.radio("O que você quer descobrir?", ["mu", "lam"], horizontal=True, key="meta_param",
                     format_func={"mu": "A taxa de atendimento (μ)", "lam": "A taxa de chegada (λ)"}.get)
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        if modelo == "mm":
            p = formulario("meta", pedir_lam=(param != "lam"), pedir_mu=(param != "mu"))
        else:
            p = formulario_mg1("metag", pedir_lam=(param != "lam"), pedir_mu=(param != "mu"))
        un = p["unidade"] if p else "hora"
        passo(5, "Qual é a meta?", "Escolha a medida e o valor que ela deve atingir.")
        tipo, arg = seletor_medida("meta", TIPOS_MM if modelo == "mm" else TIPOS_MG1, un, "A medida")
        alvo = valor_da_medida("meta", tipo, un, "Deve valer")
    with dir_:
        if p is None:
            vazio("Responda aos passos ao lado.")
            return
        if MEDIDAS[tipo][1] and arg is None or alvo is None:
            vazio("Informe a meta ao lado.")
            return
        try:
            if modelo == "mm":
                lam0 = (p["mu"] * p["s"] / 2 if not (p["K"] or p["N"]) else p["mu"]) if param == "lam" else p["lam"]
                mu0 = p["mu"] if param == "lam" else (2 * p["lam"] / p["s"] if not (p["K"] or p["N"]) else p["lam"])
                base = Fila(lam0, mu0, p["s"], p["K"], p["N"])
            else:
                lam0 = p["mu"] / 2 if param == "lam" else p["lam"]
                mu0 = p["mu"] if param == "lam" else 2 * p["lam"]
                base = FilaMG1(lam0, mu0, p["sigma"], p["erlang_k"])
            valor = parametro_para_meta(base, param, tipo, alvo, arg)
        except ValueError as e:
            aviso(f"<b>Não dá para calcular:</b> {e}")
            return
        conferencia = avaliar(replace(base, **{param: valor}), tipo, arg)
        html('<div class="sec" style="margin-top:.2rem">Resposta</div>')
        nome = "μ" if param == "mu" else "λ"
        tickets([(f"{nome} necessário", num(valor), f"clientes por {un}"),
                 ("Tempo médio entre eventos", fmt_tempo(1 / valor, un), "1 / " + nome)])
        st.caption(f"Conferência: com esse {nome}, a medida escolhida vale {formatar_medida(tipo, conferencia, un)}.")


def dimensionar_servidores():
    st.caption("Encontra o menor número de atendentes que cumpre TODOS os critérios ao mesmo tempo. "
               "Ex.: Lq ≤ 1, e pelo menos 95% do tempo com no máximo 5 na fila.")
    esq, dir_ = st.columns([5, 6], gap="large")
    with esq:
        p = formulario("srv", variar_s=True)
        un = p["unidade"] if p else "hora"
        passo(4, "Quais são os critérios?", "Cada linha é uma condição que precisa ser cumprida.")
        ini("srv_ncrit", 1)
        criterios, faltando = [], False
        for i in range(st.session_state["srv_ncrit"]):
            tipo, arg = seletor_medida(f"srv_c{i}", TIPOS_MM, un, f"Critério {i + 1}")
            c1, c2 = st.columns([1, 2.2])
            comp = c1.selectbox("deve ser", ["≤", "≥"], key=f"srv_c{i}_comp", label_visibility="collapsed")
            with c2:
                lim = valor_da_medida(f"srv_c{i}", tipo, un, "no valor")
            if lim is None or (MEDIDAS[tipo][1] and arg is None):
                faltando = True
            criterios.append((tipo, arg, comp, lim))
        c1, c2, _ = st.columns([2, 2, 2])
        if c1.button("+ Critério", key="srv_mais"):
            st.session_state["srv_ncrit"] += 1
            st.rerun()
        if c2.button("− Remover", key="srv_menos", disabled=st.session_state["srv_ncrit"] <= 1):
            st.session_state["srv_ncrit"] -= 1
            st.rerun()
    with dir_:
        if p is None or faltando:
            vazio("Responda aos passos ao lado.")
            return
        try:
            s, linhas = menor_s_criterios(p["lam"], p["mu"], criterios, p["K"], p["N"], s_max=100)
        except ValueError as e:
            aviso(f"<b>Não dá para calcular:</b> {e}")
            return
        html('<div class="sec" style="margin-top:.2rem">Resposta</div>')
        if s is None:
            aviso("Nenhum número de atendentes (até 100) cumpre todos os critérios.")
        else:
            html(f'<div class="nota">Você precisa de, no mínimo, <b>{s} atendente(s)</b>.</div>')
        cab = ["Atendentes"] + [f"{MEDIDAS[t][0]} {c} {formatar_medida(t, l, un)}" for t, a, c, l in criterios] \
            + ["Cumpre?"]
        tab = []
        for s_i, valores, ok in linhas:
            tab.append([s_i] + [formatar_medida(t, v, un) for (t, _, _, _), v in zip(criterios, valores)]
                       + ["✔" if ok else "✘"])
        st.markdown(md_tabela(cab, tab))


def aba_dimensionar():
    ferramenta = st.radio("O que você quer descobrir?",
                          ["Comparar nº de atendentes (e custos)", "Qual λ ou μ atinge uma meta?",
                           "Quantos atendentes preciso?"], horizontal=True)
    {"Comparar nº de atendentes (e custos)": dimensionar_comparar,
     "Qual λ ou μ atinge uma meta?": dimensionar_meta,
     "Quantos atendentes preciso?": dimensionar_servidores}[ferramenta]()


# --------------------------------------------------------------------------
# Aba Ferramentas
# --------------------------------------------------------------------------
def tabela_equivalencias(taxa: float, base: str):
    linhas = [[f"por {u}", fmt(converter_taxa(taxa, base, u), 4)] for u in UNIDADES]
    st.markdown(md_tabela(["Taxa equivalente", "clientes"], linhas))
    st.caption(f"Tempo médio entre eventos: {fmt_tempo(1 / taxa, base)}.")


def _ler_numeros(texto: str) -> list[float]:
    return [float(x.replace(",", ".")) for x in texto.replace(";", " ").split()]


def ferramenta_taxas():
    st.caption("Transforma o que você observou em λ ou μ (a mesma conta serve para as duas).")
    metodo = st.selectbox("O que você tem?", [
        "Número de clientes em um intervalo (ex.: 18 clientes em 10 min)",
        "Tempo médio entre chegadas ou de atendimento (ex.: 25 s por cliente)",
        "Lista de contagens por período (ex.: chegadas por dia, por mês…)",
        "Tabela de frequências (ex.: nº de ocorrências e frequência relativa)"])
    if metodo.startswith("Número"):
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Clientes", min_value=0.0, value=None, placeholder="quantidade", step=1.0, format="%g")
        t = c2.number_input("em um intervalo de", min_value=0.0, value=None, placeholder="tempo", step=1.0, format="%g")
        u = c3.selectbox("unidade", list(UNIDADES), index=1, format_func=lambda x: PLURAL[x])
        if n and t:
            html(f'<div class="nota">Taxa = <b>{fmt(taxa_por_contagem(n, t))} clientes por {u}</b></div>')
            tabela_equivalencias(taxa_por_contagem(n, t), u)
    elif metodo.startswith("Tempo"):
        c1, c2 = st.columns(2)
        t = c1.number_input("Tempo médio por cliente", min_value=0.0, value=None, placeholder="tempo", step=1.0,
                            format="%g")
        u = c2.selectbox("unidade", list(UNIDADES), index=1, format_func=lambda x: PLURAL[x])
        if t:
            html(f'<div class="nota">Taxa = <b>{fmt(taxa_por_tempo_medio(t))} clientes por {u}</b></div>')
            tabela_equivalencias(taxa_por_tempo_medio(t), u)
    elif metodo.startswith("Lista"):
        texto = st.text_area("Contagens (separe por espaço, vírgula ou linha)", placeholder="ex.: 4 7 5 6 9 3")
        if not texto.strip():
            return
        try:
            valores = _ler_numeros(texto.replace(",", " "))
            u = st.selectbox("Período de cada contagem", list(UNIDADES), index=4, format_func=lambda x: PLURAL[x])
            taxa = taxa_por_amostra(valores)
            html(f'<div class="nota">{len(valores)} períodos, total {fmt(sum(valores), 0)} → '
                 f'taxa média = <b>{fmt(taxa)} por {u}</b></div>')
            tabela_equivalencias(taxa, u)
        except ValueError:
            aviso("Digite apenas números.")
    else:
        texto = st.text_area("Uma linha por valor: o valor e a frequência (absoluta ou relativa)",
                             placeholder="ex.:\n9  0,067\n10 0,100\n11 0,200")
        if not texto.strip():
            return
        try:
            pares = []
            for linha in texto.strip().splitlines():
                nums = _ler_numeros(linha)
                if len(nums) != 2:
                    raise ValueError("Cada linha precisa ter exatamente dois números: o valor e a frequência.")
                pares.append(tuple(nums))
            u = st.selectbox("Período de cada observação", list(UNIDADES), index=4, format_func=lambda x: PLURAL[x])
            taxa = taxa_por_tabela(pares)
            html(f'<div class="nota">Média = <b>{fmt(taxa)} por {u}</b> (média ponderada pelas frequências)</div>')
            tabela_equivalencias(taxa, u)
        except ValueError as e:
            aviso(str(e))


def ferramenta_poisson():
    st.caption("Chance de ocorrerem k eventos (chegadas, atendimentos…) em um intervalo, quando a taxa é conhecida.")
    c1, c2, c3 = st.columns([1.2, 1.4, 1.4])
    taxa = c1.number_input("Taxa", min_value=0.0, value=None, placeholder="eventos", step=0.1, format="%g")
    un_t = c2.selectbox("por", list(UNIDADES), index=2, format_func=lambda u: f"por {u}", key="po_unt")
    c4, c5 = st.columns([1.2, 2.8])
    tempo = c4.number_input("Intervalo", min_value=0.0, value=1.0, step=0.5, format="%g")
    un_i = c5.selectbox("unidade do intervalo", list(UNIDADES), index=2, format_func=lambda u: PLURAL[u], key="po_uni")
    if not taxa or tempo <= 0:
        return
    m = media_no_intervalo(converter_taxa(taxa, un_t, "segundo"), converter_tempo(tempo, un_i, "segundo"))
    html(f'<div class="eco">Número médio de eventos no intervalo: m = {num(m)}</div>')
    c1, c2, c3 = st.columns([2.4, 1.2, 1.6])
    frase(c1, "Qual a chance de ocorrerem")
    op = c2.selectbox("op", ["=", "<", "≤", ">", "≥"], key="po_op", label_visibility="collapsed")
    k = c3.number_input("k", min_value=0, value=None, placeholder="k eventos", step=1, key="po_k",
                        label_visibility="collapsed")
    if k is not None:
        p = prob_poisson(op, int(k), m)
        html(f'<div class="nota">P(X {op} {int(k)}) = <b>{fmt(p, 6)}</b> ({fmt_pct(p)})</div>')
    ate = int(min(40, max(8, m + 4 * m ** 0.5 + 2)))
    acum, linhas = 0.0, []
    for j in range(ate + 1):
        pj = prob_poisson("=", j, m)
        acum += pj
        linhas.append([j, fmt(pj, 6), fmt(min(acum, 1.0), 6)])
    with st.expander("Ver tabela P(X = k)"):
        st.markdown(md_tabela(["k", "P(X = k)", "P(X ≤ k)"], linhas))


def ferramenta_little():
    st.caption("Relações que valem para QUALQUER fila (sem supor exponencial): L = λ·W, Lq = λ·Wq e W = Wq + 1/μ. "
               "Use quando o enunciado dá uma medida observada, como \"os clientes esperam em média 1 min\".")
    ini("li_un_l", "hora")
    ini("li_un_m", "hora")
    c1, c2, c3 = st.columns([2, 1.2, 1.5])
    frase(c1, "Chegadas (λ)")
    lam = c2.number_input("λ", min_value=0.0, value=None, placeholder="clientes", format="%g", key="li_lam",
                          label_visibility="collapsed")
    un_l = c3.selectbox("por", list(UNIDADES), format_func=lambda u: f"por {u}", key="li_un_l",
                        label_visibility="collapsed")
    c1, c2, c3 = st.columns([2, 1.2, 1.5])
    frase(c1, "Atendimento de um atendente (μ)")
    mu = c2.number_input("μ", min_value=0.0, value=None, placeholder="clientes", format="%g", key="li_mu",
                         label_visibility="collapsed")
    un_m = c3.selectbox("por", list(UNIDADES), format_func=lambda u: f"por {u}", key="li_un_m",
                        label_visibility="collapsed")
    c1, c2, c3 = st.columns([2, 1.2, 1.5])
    medida = c1.selectbox("Medida conhecida", ["Wq", "W", "Lq", "L"], key="li_med",
                          format_func={"Wq": "Tempo médio na fila (Wq)", "W": "Tempo médio no sistema (W)",
                                       "Lq": "Clientes na fila (Lq)", "L": "Clientes no sistema (L)"}.get)
    val = c2.number_input("valor", min_value=0.0, value=None, placeholder="valor", format="%g", key="li_val",
                          label_visibility="collapsed")
    ini("li_un_v", "minuto")
    un_v = c3.selectbox("unidade", list(UNIDADES), format_func=lambda u: PLURAL[u], key="li_un_v",
                        label_visibility="collapsed") if medida in ("W", "Wq") else None
    ini("li_un_r", "minuto")
    un_r = st.selectbox("Mostrar os tempos em", list(UNIDADES), format_func=lambda u: PLURAL[u], key="li_un_r")
    if not lam or not mu or val is None:
        return
    try:
        lam_r = converter_taxa(lam, un_l, un_r)
        mu_r = converter_taxa(mu, un_m, un_r)
        v = converter_tempo(val, un_v, un_r) if un_v else val
        d = relacoes_de_little(lam_r, mu_r, **{medida: v})
    except ValueError as e:
        aviso(str(e))
        return
    tickets([("No sistema", fmt(d["L"], 3), "clientes · L"), ("Na fila", fmt(d["Lq"], 3), "clientes · Lq"),
             ("Tempo no sistema", fmt_tempo(d["W"], un_r), "W"), ("Tempo na fila", fmt_tempo(d["Wq"], un_r), "Wq")])


def ferramenta_kendall():
    st.caption("Decodifica a notação A/B/m/C/K/N e diz se este projeto resolve o modelo.")
    exemplos = ["(digitar abaixo)", "M/M/1", "M/M/4/FCFS/12", "M/M/2/FCFS/∞/30", "M/G/1", "D/M/3/LIFO/20/∞"]
    escolha = st.selectbox("Exemplos de notação", exemplos)
    texto = st.text_input("Notação de Kendall", placeholder="ex.: M/M/2/FCFS/10")
    notacao = texto if escolha == exemplos[0] else escolha
    if not notacao.strip():
        return
    try:
        k = decodificar(notacao)
    except ValueError as e:
        aviso(str(e))
        return
    st.markdown("\n".join(f"- {l}" for l in k.explicar()))
    params, msg = k.modelo_do_projeto()
    if params:
        html(f'<div class="nota">{msg} Use a aba Calculadora.</div>')
    elif k.A.upper() == "M" and k.B.upper() in ("G", "D") and k.m == 1:
        html('<div class="nota">Esse modelo é um M/G/1: use a aba Calculadora → M/G/1.</div>')
    else:
        aviso(msg)


def aba_ferramentas():
    ferramenta = st.radio("Ferramenta", ["Calcular λ e μ a partir de dados", "Contagens de Poisson",
                                         "Lei de Little", "Notação de Kendall"], horizontal=True)
    {"Calcular λ e μ a partir de dados": ferramenta_taxas, "Contagens de Poisson": ferramenta_poisson,
     "Lei de Little": ferramenta_little, "Notação de Kendall": ferramenta_kendall}[ferramenta]()


# --------------------------------------------------------------------------
# Aba Teoria
# --------------------------------------------------------------------------
def aba_teoria():
    secao = st.radio("Seção", ["Modelos e fórmulas", "Relações gerais", "Como ler um enunciado", "Glossário",
                               "Notação de Kendall"], horizontal=True)
    if secao == "Modelos e fórmulas":
        titulos = {m["id"]: m["titulo"] for m in TEORIA_MODELOS}
        mid = st.selectbox("Modelo", list(titulos), format_func=titulos.get)
        m = next(x for x in TEORIA_MODELOS if x["id"] == mid)
        html(f'<div class="sec" style="margin-top:.4rem">{m["titulo"]}</div>')
        html(f'<div class="nota"><b>Quando usar:</b> {m["quando"]}</div>')
        st.markdown("**Pressupostos**\n\n" + "\n".join(f"- {p}" for p in m["pressupostos"]))
        st.markdown("**Fórmulas**")
        for rotulo, tex in m["formulas"]:
            if rotulo:
                st.caption(rotulo)
            st.latex(tex)
        st.info(m["dica"])
    elif secao == "Relações gerais":
        st.markdown("Valem para qualquer fila estável, sem supor distribuição exponencial.")
        for rotulo, tex in RELACOES:
            st.caption(rotulo)
            st.latex(tex)
    elif secao == "Como ler um enunciado":
        st.markdown("O que cada trecho do enunciado vira na calculadora:")
        st.markdown(md_tabela(["O enunciado diz", "Significa"], [[a, b] for a, b in COMO_LER]))
    elif secao == "Glossário":
        st.markdown(md_tabela(["Termo", "O que é"], [[f"**{a}**", b] for a, b in GLOSSARIO]))
    else:
        st.markdown(KENDALL)
        st.markdown(md_tabela(["Notação", "Significado"], [
            ["M/M/1", "1 atendente, chegadas e atendimento exponenciais, sem limites"],
            ["M/M/3/FCFS/10/∞", "3 atendentes, FIFO, capacidade K = 10, população infinita (M/M/s/K)"],
            ["M/M/1/FCFS/∞/20", "1 atendente, população finita de 20 (M/M/1/N)"],
            ["M/D/1", "atendimento constante (caso de M/G/1 com σ = 0)"],
            ["M/G/1", "atendimento com distribuição qualquer"]]))


# --------------------------------------------------------------------------
# Página
# --------------------------------------------------------------------------
html('<div class="topo"><div class="olho">Otimização II · Teoria das Filas</div>'
     '<div class="titulo">Calculadora de filas</div>'
     '<div class="sub">M/M/1 · M/M/s · M/M/1/K · M/M/s/K · M/M/1/N · M/M/s/N · M/G/1 · prioridades — '
     'preencha a ficha à esquerda, o resultado aparece à direita.</div></div>')

t1, t2, t3, t4 = st.tabs(["Calculadora", "Dimensionar", "Ferramentas", "Teoria"])
with t1:
    aba_calculadora()
with t2:
    aba_dimensionar()
with t3:
    aba_ferramentas()
with t4:
    aba_teoria()
