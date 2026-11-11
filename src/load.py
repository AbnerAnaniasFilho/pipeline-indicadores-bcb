"""Carga dos dados no PostgreSQL com upsert."""

import logging
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text

from src.config import SERIES, montar_url_banco
from src.extract import extrair_serie

ARQUIVO_SCHEMA = Path(__file__).parent.parent / "sql" / "01_schema.sql"

SQL_UPSERT_SERIE = text(
    """
    INSERT INTO serie (codigo, nome, unidade, periodicidade)
    VALUES (:codigo, :nome, :unidade, :periodicidade)
    ON CONFLICT (codigo) DO UPDATE
    SET nome = EXCLUDED.nome,
        unidade = EXCLUDED.unidade,
        periodicidade = EXCLUDED.periodicidade
    """
)

SQL_UPSERT_OBSERVACAO = text(
    """
    INSERT INTO observacao (codigo_serie, data, valor)
    VALUES (:codigo_serie, :data, :valor)
    ON CONFLICT (codigo_serie, data) DO UPDATE
    SET valor = EXCLUDED.valor,
        carregado_em = now()
    """
)

logger = logging.getLogger(__name__)


def criar_engine():
    """Cria a engine do SQLAlchemy para o banco do projeto."""
    return create_engine(montar_url_banco())


def criar_tabelas(engine):
    """Executa o sql/01_schema.sql, que cria as tabelas se ainda não existirem."""
    comandos = ARQUIVO_SCHEMA.read_text(encoding="utf-8")
    with engine.begin() as conexao:
        conexao.execute(text(comandos))


def salvar_series(engine, series):
    """Grava o cadastro das séries (lista de dicionários) com upsert."""
    with engine.begin() as conexao:
        conexao.execute(SQL_UPSERT_SERIE, series)


def salvar_observacoes(engine, codigo_serie, tabela):
    """Grava as observações de uma série com upsert.

    Recebe o DataFrame devolvido pela extração (colunas data e valor) e
    devolve a quantidade de linhas enviadas ao banco.
    """
    registros = tabela.assign(codigo_serie=codigo_serie).to_dict("records")
    if not registros:
        return 0
    with engine.begin() as conexao:
        conexao.execute(SQL_UPSERT_OBSERVACAO, registros)
    return len(registros)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    engine = criar_engine()
    criar_tabelas(engine)
    salvar_series(engine, SERIES)

    dolar = extrair_serie(1, date(2015, 1, 1), date.today())
    enviadas = salvar_observacoes(engine, 1, dolar)

    with engine.connect() as conexao:
        total = conexao.execute(text("SELECT count(*) FROM observacao")).scalar()
    logger.info("Linhas enviadas: %s | linhas na tabela: %s", enviadas, total)
