"""Pipeline incremental: extrai as séries do Banco Central e grava no PostgreSQL.

Rode na raiz do projeto com: python -m src.pipeline
"""

import logging
from datetime import date, timedelta
from pathlib import Path

from src.config import DATA_INICIAL_HISTORICO, SERIES
from src.extract import extrair_serie
from src.load import (
    buscar_ultima_data,
    criar_engine,
    criar_tabelas,
    salvar_observacoes,
    salvar_series,
)

ARQUIVO_LOG = Path(__file__).parent.parent / "logs" / "pipeline.log"
FORMATO_LOG = "%(asctime)s %(levelname)s %(message)s"

logger = logging.getLogger(__name__)


def configurar_logging():
    """Envia as mensagens de log para o console e para logs/pipeline.log."""
    ARQUIVO_LOG.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=FORMATO_LOG,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
        ],
    )


def calcular_data_inicial(ultima_data):
    """Decide a partir de que dia buscar os dados de uma série."""
    if ultima_data is None:
        return DATA_INICIAL_HISTORICO
    return ultima_data + timedelta(days=1)


def processar_serie(engine, serie):
    """Faz a carga incremental de uma série e devolve quantas linhas gravou."""
    codigo = serie["codigo"]
    ultima_data = buscar_ultima_data(engine, codigo)
    data_inicial = calcular_data_inicial(ultima_data)
    logger.info(
        "Série %s: última data no banco é %s; buscando a partir de %s",
        codigo,
        ultima_data,
        data_inicial,
    )
    tabela = extrair_serie(codigo, data_inicial, date.today())
    return salvar_observacoes(engine, codigo, tabela)


def executar():
    """Roda o pipeline para todas as séries; a falha de uma não para as outras."""
    engine = criar_engine()
    criar_tabelas(engine)
    salvar_series(engine, SERIES)

    falhas = 0
    for serie in SERIES:
        try:
            linhas = processar_serie(engine, serie)
            logger.info(
                "Série %s (%s): linhas gravadas: %s",
                serie["codigo"],
                serie["nome"],
                linhas,
            )
        except Exception:
            falhas += 1
            logger.exception("Série %s (%s): falhou", serie["codigo"], serie["nome"])
    logger.info("Pipeline concluído: %s séries, %s com falha", len(SERIES), falhas)


if __name__ == "__main__":
    configurar_logging()
    executar()
