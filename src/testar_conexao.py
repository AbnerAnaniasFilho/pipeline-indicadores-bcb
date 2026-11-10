"""Testa a conexão com o PostgreSQL.

Rode na raiz do projeto com: python -m src.testar_conexao
"""

import logging

from sqlalchemy import create_engine, text

from src.config import montar_url_banco

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def testar_conexao():
    """Abre uma conexão com o banco e registra a versão do PostgreSQL."""
    engine = create_engine(montar_url_banco())
    with engine.connect() as conexao:
        versao = conexao.execute(text("SELECT version()")).scalar()
    logger.info("Conexão OK: %s", versao)


if __name__ == "__main__":
    testar_conexao()
