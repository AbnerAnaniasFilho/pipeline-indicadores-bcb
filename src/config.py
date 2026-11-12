"""Configurações do projeto: lê as variáveis do arquivo .env."""

import os
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import URL

# Lê o arquivo .env e coloca as variáveis no ambiente deste processo.
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Primeiro dia do histórico: ponto de partida quando o banco está vazio.
DATA_INICIAL_HISTORICO = date(2015, 1, 1)

# Séries do Banco Central que o pipeline acompanha (códigos do SGS).
SERIES = [
    {
        "codigo": 1,
        "nome": "Dólar comercial (venda)",
        "unidade": "R$",
        "periodicidade": "diária",
    },
    {
        "codigo": 432,
        "nome": "Meta Selic definida pelo Copom",
        "unidade": "% a.a.",
        "periodicidade": "diária",
    },
    {
        "codigo": 433,
        "nome": "IPCA",
        "unidade": "% no mês",
        "periodicidade": "mensal",
    },
]


def montar_url_banco():
    """Monta a URL de conexão do SQLAlchemy com as variáveis do .env."""
    return URL.create(
        "postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    ) 