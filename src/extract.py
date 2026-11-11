"""Extração de séries da API SGS do Banco Central."""

import logging
from datetime import date, timedelta

import pandas as pd
import requests

URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
FORMATO_DATA = "%d/%m/%Y"
ANOS_POR_JANELA = 3
TIMEOUT_SEGUNDOS = 30

logger = logging.getLogger(__name__)


def gerar_janelas(data_inicial, data_final, anos_por_janela=ANOS_POR_JANELA):
    """Divide o período em janelas de no máximo `anos_por_janela` anos.

    Cada janela termina em 31 de dezembro, menos a última, que termina na
    data final. Devolve uma lista de tuplas (inicio, fim), sem sobreposição.
    Se a data inicial for depois da final, devolve uma lista vazia.
    """
    janelas = []
    inicio = data_inicial
    while inicio <= data_final:
        fim_do_bloco = date(inicio.year + anos_por_janela - 1, 12, 31)
        fim = min(fim_do_bloco, data_final)
        janelas.append((inicio, fim))
        inicio = fim + timedelta(days=1)
    return janelas


def buscar_janela(codigo, inicio, fim):
    """Busca na API as observações de uma série entre duas datas.

    Devolve a lista de dicionários da API, ou uma lista vazia quando não há
    dados no período (nesse caso a API responde com o status 404).
    """
    parametros = {
        "formato": "json",
        "dataInicial": inicio.strftime(FORMATO_DATA),
        "dataFinal": fim.strftime(FORMATO_DATA),
    }
    resposta = requests.get(
        URL_SGS.format(codigo=codigo),
        params=parametros,
        timeout=TIMEOUT_SEGUNDOS,
    )
    if resposta.status_code == 404:
        return []
    resposta.raise_for_status()
    return resposta.json()


def converter_resposta(dados):
    """Converte a lista da API em um DataFrame com data (date) e valor (número)."""
    tabela = pd.DataFrame(dados, columns=["data", "valor"])
    tabela["data"] = pd.to_datetime(tabela["data"], format=FORMATO_DATA).dt.date
    tabela["valor"] = pd.to_numeric(tabela["valor"])
    return tabela


def extrair_serie(codigo, data_inicial, data_final):
    """Extrai uma série da API, janela por janela, e devolve um DataFrame."""
    registros = []
    for inicio, fim in gerar_janelas(data_inicial, data_final):
        logger.info("Série %s: buscando de %s a %s", codigo, inicio, fim)
        registros.extend(buscar_janela(codigo, inicio, fim))
    return converter_resposta(registros)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    dolar = extrair_serie(1, date(2015, 1, 1), date.today())
    logger.info("Total de observações: %s", len(dolar))
    logger.info("Primeiras linhas:\n%s", dolar.head(3))
    logger.info("Últimas linhas:\n%s", dolar.tail(3))
