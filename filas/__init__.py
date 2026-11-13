"""Teoria das Filas — modelos M/M. Veja README.md."""
from .modelos import (
    Fila, Resultado, FilaInstavel, NaoDisponivel, METRICAS,
    custo_total, comparar_servidores, lambda_para_meta, menor_s_para_meta,
)

__all__ = [
    "Fila", "Resultado", "FilaInstavel", "NaoDisponivel", "METRICAS",
    "custo_total", "comparar_servidores", "lambda_para_meta", "menor_s_para_meta",
]
