-- Tabelas do pipeline de indicadores do Banco Central.
-- Pode ser executado várias vezes: só cria o que ainda não existe.

-- Cadastro das séries acompanhadas.
CREATE TABLE IF NOT EXISTS serie (
    codigo INTEGER NOT NULL,
    nome TEXT NOT NULL,
    unidade TEXT NOT NULL,
    periodicidade TEXT NOT NULL,
    PRIMARY KEY (codigo)
);

-- Uma linha por série e por dia. A chave primária composta impede que a
-- mesma data seja gravada duas vezes para a mesma série.
CREATE TABLE IF NOT EXISTS observacao (
    codigo_serie INTEGER NOT NULL REFERENCES serie (codigo),
    data         DATE NOT NULL,
    valor        NUMERIC NOT NULL,
    carregado_em TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (codigo_serie, data)
);
