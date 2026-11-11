"""Testes das funções puras de src/extract.py (não chamam a API)."""

from datetime import date

import pytest

from src.extract import converter_resposta, gerar_janelas


def test_gerar_janelas_intervalo_curto_cabe_em_uma_janela():
    janelas = gerar_janelas(date(2024, 3, 1), date(2024, 6, 30))

    assert janelas == [(date(2024, 3, 1), date(2024, 6, 30))]


def test_gerar_janelas_divide_intervalo_longo_sem_sobrepor():
    janelas = gerar_janelas(date(2015, 1, 1), date(2021, 6, 30))

    assert janelas == [
        (date(2015, 1, 1), date(2017, 12, 31)),
        (date(2018, 1, 1), date(2020, 12, 31)),
        (date(2021, 1, 1), date(2021, 6, 30)),
    ]


def test_gerar_janelas_sem_nada_para_buscar():
    # Data inicial depois da final: acontece quando o banco já está em dia.
    janelas = gerar_janelas(date(2024, 1, 2), date(2024, 1, 1))

    assert janelas == []


def test_converter_resposta_converte_data_e_valor():
    dados = [
        {"data": "02/01/2024", "valor": "4.8916"},
        {"data": "03/01/2024", "valor": "4.9212"},
    ]

    tabela = converter_resposta(dados)

    assert list(tabela["data"]) == [date(2024, 1, 2), date(2024, 1, 3)]
    assert list(tabela["valor"]) == pytest.approx([4.8916, 4.9212])


def test_converter_resposta_lista_vazia():
    tabela = converter_resposta([])

    assert len(tabela) == 0
    assert list(tabela.columns) == ["data", "valor"]


def test_gerar_janelas_intervalo_de_um_dia():
    janelas = gerar_janelas(date(2024, 5, 10), date(2024, 5, 10))

    assert janelas == [(date(2024, 5, 10), date(2024, 5, 10))]