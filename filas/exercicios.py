"""
Exercícios M/M do PDF "Teoria das filas – Modelo MMs" (P108 – Otimização II),
resolvidos com o mesmo motor da calculadora.

Cada item traz a resposta calculada, a fórmula usada e, quando o slide
publica o gabarito, uma conferência automática (`confere`).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from .modelos import Fila, lambda_para_meta
from .unidades import (converter_taxa, converter_tempo, fmt, taxa_por_amostra,
                       taxa_por_contagem, taxa_por_tempo_medio)

DIAS_POR_MES = 30


@dataclass
class Item:
    letra: str
    pergunta: str
    valor: Optional[float]      # None quando a resposta é uma tabela
    unidade: str                # texto mostrado depois do valor ('dias', 'clientes', '')
    formula: str
    gabarito: Optional[str] = None          # valor do slide, ex.: "0,0233"
    tabela: Optional[list[tuple]] = None    # linhas, para itens com tabela
    cabecalho: Optional[tuple] = None

    @property
    def resposta(self) -> str:
        if self.valor is None:
            return "ver tabela"
        casas = 4 if self.unidade in ("", "prob.") else 3
        sufixo = "" if self.unidade == "prob." else self.unidade
        return f"{fmt(self.valor, casas)} {sufixo}".strip()

    @property
    def confere(self) -> Optional[bool]:
        """True/False comparando com o gabarito do slide (None se o slide não traz)."""
        if self.gabarito is None or self.valor is None:
            return None
        esperado = float(self.gabarito.replace(",", "."))
        casas = len(self.gabarito.split(",")[1]) if "," in self.gabarito else 0
        return abs(self.valor - esperado) <= 0.5 * 10 ** -casas + 1e-4


@dataclass
class Exercicio:
    id: str
    titulo: str
    enunciado: str
    dados: dict[str, str]
    itens: list[Item] = field(default_factory=list)
    observacao: str = ""


# Motores danificados por mês (30 meses) — dados do exercício 1 de M/M/1
MOTORES_DANIFICADOS = [
    9, 8, 11, 10, 8, 11, 13, 13, 12, 12,
    9, 12, 11, 13, 10, 13, 10, 12, 11, 12,
    11, 12, 11, 13, 9, 11, 13, 10, 10, 10,
]


# --------------------------------------------------------------------------
def intro_taxas() -> Exercicio:
    lam_min = taxa_por_contagem(6, 5)                         # 6 clientes em 5 min
    mu_min = taxa_por_tempo_medio(converter_tempo(40, "segundo", "minuto"))
    return Exercicio(
        id="taxas", titulo="Introdução — taxas λ e μ (slide 29)",
        enunciado="Em 5 minutos chegam 6 clientes. Cada atendimento leva em média 40 segundos. "
                  "Qual a taxa de chegada e a taxa de atendimento?",
        dados={"Chegadas": "6 clientes em 5 min", "Atendimento": "40 s por cliente"},
        itens=[
            Item("a", "Taxa de chegada λ", lam_min, "clientes/min", "λ = nº de clientes ÷ tempo observado"),
            Item("a (em horas)", "λ por hora", converter_taxa(lam_min, "minuto", "hora"), "clientes/h",
                 "multiplicar por 60"),
            Item("b", "Taxa de atendimento μ", mu_min, "clientes/min", "μ = 1 ÷ tempo médio de serviço (TMS)"),
            Item("b (em horas)", "μ por hora", converter_taxa(mu_min, "minuto", "hora"), "clientes/h",
                 "multiplicar por 60"),
        ],
    )


def mm1_motores() -> Exercicio:
    lam = taxa_por_amostra(MOTORES_DANIFICADOS)       # 11 motores/mês
    rho = 0.88
    mu = lam / rho                                    # ρ = λ/μ  ->  μ = λ/ρ
    f = Fila(lam, mu)
    r = f.resultado()
    dias = DIAS_POR_MES
    freq = Counter(MOTORES_DANIFICADOS)
    n = len(MOTORES_DANIFICADOS)
    tabela = [(k, freq[k], fmt(freq[k] / n, 4)) for k in sorted(freq)]
    return Exercicio(
        id="mm1-motores", titulo="M/M/1 — Exemplo 1 (motores elétricos)",
        enunciado="Motores danificados por mês durante 30 meses chegam à seção de manutenção, "
                  "que opera com taxa de ocupação de 88%.",
        dados={"λ": f"{fmt(lam, 2)} motores/mês (média dos 30 meses)",
               "ρ": "0,88 (dado)", "μ": f"{fmt(mu, 2)} motores/mês (μ = λ/ρ)"},
        itens=[
            Item("a", "Distribuição de frequência relativa do nº de motores danificados", None, "",
                 "frequência relativa = nº de meses com k motores ÷ 30",
                 tabela=tabela, cabecalho=("Motores/mês", "Meses", "Freq. relativa")),
            Item("b", "Tempo médio fora de serviço (W)", r.W * dias, "dias", "W = 1/(μ−λ)  (× 30 dias/mês)"),
            Item("c", "Nº médio de motores aguardando reparo (Lq)", r.Lq, "motores", "Lq = λ²/[μ(μ−λ)]"),
            Item("d", "Tempo médio de espera para iniciar o reparo (Wq)", r.Wq * dias, "dias",
                 "Wq = λ/[μ(μ−λ)]  (× 30 dias/mês)"),
            Item("e", "Nº médio de motores fora de serviço (L)", r.L, "motores", "L = λ/(μ−λ)"),
            Item("f", "Probabilidade de o sistema estar ocioso (P0)", r.P0, "prob.", "P0 = 1 − ρ"),
            Item("g", "Probabilidade de o sistema estar ocupado", 1 - r.P0, "prob.", "ρ = λ/μ"),
            Item("h", "P(W > 1 mês)", f.P_W_maior(1), "prob.", "P(W>t) = e^(−μ(1−ρ)t)"),
            Item("i", "P(Wq > 1 mês)", f.P_Wq_maior(1), "prob.", "P(Wq>t) = ρ·e^(−μ(1−ρ)t)"),
        ],
        observacao="O slide não informa a unidade de t nos itens h e i; foi adotado 1 mês, "
                   "a mesma unidade das taxas. No item e, o slide pede \"em dias\" por engano: "
                   "L é um número de motores.",
    )


def mm1_barbearia() -> Exercicio:
    lam = taxa_por_tempo_medio(converter_tempo(20, "minuto", "hora"))   # 3 por hora
    mu = taxa_por_tempo_medio(converter_tempo(15, "minuto", "hora"))    # 4 por hora
    f = Fila(lam, mu)
    r = f.resultado()
    meta_w = 1.25
    lam_novo = lambda_para_meta(f, "W", meta_w)
    return Exercicio(
        id="mm1-barbearia", titulo="M/M/1 — Exemplo 2 (barbearia)",
        enunciado="Um barbeiro, clientes chegam a cada 20 min em média e cada corte leva 15 min.",
        dados={"λ": "3 clientes/h (1 a cada 20 min)", "μ": "4 clientes/h (1 a cada 15 min)"},
        itens=[
            Item("a", "Probabilidade de o cliente não esperar (P0)", r.P0, "prob.", "P0 = 1 − λ/μ", "0,25"),
            Item("b (L)", "Nº esperado de clientes no salão (L)", r.L, "clientes", "L = λ/(μ−λ)", "3"),
            Item("b (Lq)", "Nº esperado de clientes na fila (Lq)", r.Lq, "clientes", "Lq = λ²/[μ(μ−λ)]", "2,25"),
            Item("c", "Tempo médio no salão (W)", r.W, "h", "W = 1/(μ−λ)", "1"),
            Item("d", "Tempo médio na fila (Wq)", r.Wq * 60, "min", "Wq = λ/[μ(μ−λ)]", "45"),
            Item("e", "P(esperar mais de 1 h na fila) = P(Wq > 1)", f.P_Wq_maior(1), "prob.",
                 "P(Wq>t) = ρ·e^(−μ(1−ρ)t)"),
            Item("f", "P(ficar mais de 1 h no salão) = P(W > 1)", f.P_W_maior(1), "prob.",
                 "P(W>t) = e^(−μ(1−ρ)t)"),
            Item("g", f"λ para o 2º barbeiro se justificar (W = {meta_w} h)", lam_novo, "clientes/h",
                 "W = 1/(μ−λ)  →  λ = μ − 1/W", "3,2"),
        ],
    )


def mms_sobrecarga() -> Exercicio:
    f = Fila(30, 20, s=2)
    r = f.resultado()
    return Exercicio(
        id="mms-sobrecarga", titulo="M/M/s — Exemplo 1 (passar de 1 para 2 canais)",
        enunciado="Chegam 30 clientes/h e cada atendente atende 20/h. Será criado um segundo canal, com fila única.",
        dados={"λ": "30 clientes/h", "μ": "20 clientes/h por canal", "s": "2 canais"},
        itens=[
            Item("a", "Nº médio de clientes na fila (Lq)", r.Lq, "clientes", "Lq = P0·(λ/μ)ˢ·ρ / [s!(1−ρ)²]"),
            Item("b", "Tempo médio na fila (Wq)", r.Wq * 60, "min", "Wq = Lq/λ"),
            Item("c", "Nº médio de clientes no sistema (L)", r.L, "clientes", "L = Lq + λ/μ"),
            Item("d", "Tempo médio no sistema (W)", r.W * 60, "min", "W = Wq + 1/μ"),
            Item("e", "P(W > 12 min)", f.P_W_maior(12 / 60), "prob.", "fórmula de P(W>t) do M/M/s"),
            Item("f", "P(Wq > 6 min)", f.P_Wq_maior(6 / 60), "prob.", "P(Wq>t) = [1−P(Wq=0)]·e^(−sμ(1−ρ)t)"),
            Item("g", "P(3 clientes no sistema)", f.P(3), "prob.", "Pn = (λ/μ)ⁿ/(s!·s^(n−s)) · P0, para n ≥ s"),
        ],
    )


def mms_banco() -> Exercicio:
    f = Fila(0.6, 0.5, s=3)
    r = f.resultado()
    return Exercicio(
        id="mms-banco", titulo="M/M/s — Exemplo 2 (agência bancária)",
        enunciado="λ = 0,60 clientes/min, atendimento médio de 2 min. O gerente coloca mais 2 caixas (total de 3).",
        dados={"λ": "0,60 clientes/min", "μ": "0,5 clientes/min por caixa (1/2 min)", "s": "3 caixas"},
        itens=[
            Item("a", "Taxa de ocupação (ρ)", r.rho, "prob.", "ρ = λ/(s·μ)", "0,4"),
            Item("b", "Nº médio de clientes no sistema (L)", r.L, "clientes", "L = Lq + λ/μ", "1,29"),
            Item("c", "Nº médio de clientes na fila (Lq)", r.Lq, "clientes", "Lq = P0·(λ/μ)ˢ·ρ / [s!(1−ρ)²]", "0,094"),
            Item("d", "Probabilidade de o sistema estar vazio (P0)", r.P0, "prob.", "P0 = 1/[Σ(λ/μ)ⁿ/n! + (λ/μ)ˢ/(s!(1−ρ))]", "0,294"),
            Item("e", "P(mais de 5 clientes no sistema)", f.P_mais_que(5), "prob.", "P(n>5) = 1 − Σ Pn (n = 0..5)", "0,0091"),
            Item("f", "Tempo médio de espera na fila (Wq)", r.Wq, "min", "Wq = Lq/λ", "0,157"),
            Item("g", "Tempo médio no sistema (W)", r.W, "min", "W = Wq + 1/μ", "2,16"),
            Item("h", "P(W > 3 min)", f.P_W_maior(3), "prob.", "fórmula de P(W>t) do M/M/s", "0,2506"),
            Item("i", "P(Wq > 2 min)", f.P_Wq_maior(2), "prob.", "P(Wq>t) = [1−P(Wq=0)]·e^(−sμ(1−ρ)t)", "0,0233"),
        ],
        observacao="No item e o slide traz 0,0091; o valor exato é 0,0090 (diferença de arredondamento).",
    )


def todos() -> list[Exercicio]:
    return [intro_taxas(), mm1_motores(), mm1_barbearia(), mms_sobrecarga(), mms_banco()]

