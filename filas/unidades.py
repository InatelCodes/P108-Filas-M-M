"""
Unidades de tempo, conversão de taxas e formatação de números (pt-BR).

Convenção: 1 mês = 30 dias.
"""
from __future__ import annotations

import re
from typing import Iterable

# nome -> segundos
UNIDADES = {"segundo": 1, "minuto": 60, "hora": 3600, "dia": 86400, "mês": 30 * 86400}
PLURAL = {"segundo": "segundos", "minuto": "minutos", "hora": "horas", "dia": "dias", "mês": "meses"}
ABREV = {"segundo": "s", "minuto": "min", "hora": "h", "dia": "dias", "mês": "mês"}

_APELIDOS = {
    "s": "segundo", "seg": "segundo", "segundo": "segundo", "segundos": "segundo",
    "min": "minuto", "minuto": "minuto", "minutos": "minuto",
    "h": "hora", "hora": "hora", "horas": "hora",
    "d": "dia", "dia": "dia", "dias": "dia",
    "mes": "mês", "mês": "mês", "meses": "mês",
}


def normalizar_unidade(texto: str) -> str:
    """Aceita 'min', 'minutos', 'h', 'horas'... e devolve o nome canônico."""
    chave = texto.strip().lower()
    if chave not in _APELIDOS:
        raise ValueError(f"Unidade desconhecida: '{texto}'. Use segundo, minuto, hora, dia ou mês.")
    return _APELIDOS[chave]


# ---- conversões ----------------------------------------------------------
def converter_tempo(valor: float, de: str, para: str) -> float:
    """3 horas -> 180 minutos:  converter_tempo(3, 'hora', 'minuto')."""
    return valor * UNIDADES[de] / UNIDADES[para]


def converter_taxa(valor: float, de: str, para: str) -> float:
    """30 por hora -> 0,5 por minuto:  converter_taxa(30, 'hora', 'minuto')."""
    return valor * UNIDADES[para] / UNIDADES[de]


def taxa_por_contagem(quantidade: float, intervalo: float) -> float:
    """λ = clientes que chegam ÷ tempo observado (ex.: 6 clientes em 5 min -> 1,2 por min)."""
    if intervalo <= 0:
        raise ValueError("O intervalo de observação precisa ser maior que zero.")
    return quantidade / intervalo


def taxa_por_tempo_medio(tempo_medio: float) -> float:
    """λ = 1 ÷ tempo médio entre chegadas (ou μ = 1 ÷ tempo médio de serviço)."""
    if tempo_medio <= 0:
        raise ValueError("O tempo médio precisa ser maior que zero.")
    return 1.0 / tempo_medio


def taxa_por_amostra(valores: Iterable[float]) -> float:
    """Média de uma lista de contagens por período (ex.: motores danificados por mês)."""
    valores = list(valores)
    if not valores:
        raise ValueError("A lista de valores está vazia.")
    return sum(valores) / len(valores)


def taxa_por_tabela(pares: Iterable[tuple]) -> float:
    """
    Média ponderada de uma tabela de frequências [(valor, frequência), ...]. As frequências podem ser
    absolutas (nº de períodos) ou relativas (0,067…); a média é a mesma.
    Ex.: [(9, 0,067), (10, 0,100), ...] -> nº médio de ocorrências por período (λ).
    """
    pares = [(float(v), float(f)) for v, f in pares]
    total = sum(f for _, f in pares)
    if not pares or total <= 0:
        raise ValueError("A tabela precisa ter ao menos uma linha com frequência maior que zero.")
    return sum(v * f for v, f in pares) / total


_PADRAO_TAXA = re.compile(r"^\s*([\d.,]+)\s*([a-zçêé]*)\s*$", re.IGNORECASE)


def ler_taxa(texto: str, unidade_base: str) -> float:
    """
    Lê um número digitado e devolve a taxa por `unidade_base`.

        ler_taxa("3", "hora")       -> 3,0   (já é uma taxa: 3 por hora)
        ler_taxa("20 min", "hora")  -> 3,0   (tempo médio de 20 min -> 3 por hora)
        ler_taxa("40s", "minuto")   -> 1,5   (40 segundos por cliente -> 1,5 por min)
    """
    m = _PADRAO_TAXA.match(texto)
    if not m:
        raise ValueError(f"Não entendi '{texto}'. Exemplos: 3  |  20 min  |  40s")
    numero = float(m.group(1).replace(",", "."))
    if m.group(2) == "":
        return numero
    unidade = normalizar_unidade(m.group(2))
    return taxa_por_tempo_medio(converter_tempo(numero, unidade, unidade_base))


# ---- formatação ----------------------------------------------------------
def fmt(valor: float, casas: int = 4) -> str:
    """Número com vírgula decimal: 0.25 -> '0,2500'."""
    return f"{valor:.{casas}f}".replace(".", ",")


def fmt_pct(prob: float, casas: int = 2) -> str:
    return fmt(prob * 100, casas) + "%"


def fmt_tempo(valor: float, unidade: str) -> str:
    """Formata tempos com unidades compostas (ex.: 1 h 12 min; 12 min 3 s)."""
    segundos = valor * UNIDADES[unidade]
    if segundos == 0:
        return "0 s"
    sinal = "−" if segundos < 0 else ""
    restante = abs(segundos)
    partes = []
    for nome in ("mês", "dia", "hora", "minuto"):
        fator = UNIDADES[nome]
        quantidade = int(restante // fator)
        if quantidade:
            partes.append(f"{quantidade} {ABREV[nome]}")
            restante -= quantidade * fator
    if restante >= 0.005 or not partes:
        casas = 2 if restante < 10 else 1
        numero = fmt(restante, casas).rstrip("0").rstrip(",")
        partes.append(f"{numero} s")
    return sinal + " e ".join(partes[:2] if len(partes) > 2 else partes)
