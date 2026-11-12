"""Testes da função pura de src/pipeline.py (não usam o banco nem a API)."""

from datetime import date

from src.pipeline import calcular_data_inicial


def test_calcular_data_inicial_sem_dados_comeca_no_inicio_do_historico():
    assert calcular_data_inicial(None) == date(2015, 1, 1)


def test_calcular_data_inicial_com_dados_comeca_no_dia_seguinte():
    assert calcular_data_inicial(date(2024, 5, 10)) == date(2024, 5, 11)


def test_calcular_data_inicial_vira_o_mes():
    assert calcular_data_inicial(date(2024, 1, 31)) == date(2024, 2, 1)
