"""Carga dos dados no PostgreSQL com upsert."""

from pathlib import Path

from sqlalchemy import create_engine, text

from src.config import montar_url_banco

PASTA_SQL = Path(__file__).parent.parent / "sql"
ARQUIVOS_SQL = ["01_schema.sql", "02_views.sql"]

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

SQL_ULTIMA_DATA = text(
    "SELECT max(data) FROM observacao WHERE codigo_serie = :codigo_serie"
)


def criar_engine():
    """Cria a engine do SQLAlchemy para o banco do projeto."""
    return create_engine(montar_url_banco())


def executar_arquivo_sql(engine, nome_arquivo):
    """Executa todos os comandos de um arquivo da pasta sql/."""
    comandos = (PASTA_SQL / nome_arquivo).read_text(encoding="utf-8")
    with engine.begin() as conexao:
        conexao.execute(text(comandos))


def criar_estrutura(engine):
    """Cria as tabelas e as views do projeto; pode ser chamada várias vezes."""
    for nome_arquivo in ARQUIVOS_SQL:
        executar_arquivo_sql(engine, nome_arquivo)


def salvar_series(engine, series):
    """Grava o cadastro das séries (lista de dicionários) com upsert."""
    with engine.begin() as conexao:
        conexao.execute(SQL_UPSERT_SERIE, series)


def buscar_ultima_data(engine, codigo_serie):
    """Devolve a data mais recente já gravada para a série, ou None se não houver."""
    with engine.connect() as conexao:
        resultado = conexao.execute(SQL_ULTIMA_DATA, {"codigo_serie": codigo_serie})
        return resultado.scalar()


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
