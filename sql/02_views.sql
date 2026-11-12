-- Views analíticas lidas pelo Power BI.
-- O arquivo apaga e recria as views, então pode ser executado várias vezes.

DROP VIEW IF EXISTS vw_juro_real_mensal;
DROP VIEW IF EXISTS vw_ipca_12m;
DROP VIEW IF EXISTS vw_dolar_diario;


-- Dólar por dia útil, com a variação em % contra a cotação anterior e a
-- média móvel das últimas 7 cotações (a linha atual e as 6 anteriores).
CREATE VIEW vw_dolar_diario AS
SELECT
    data,
    valor AS cotacao,
    ROUND((valor / LAG(valor) OVER (ORDER BY data) - 1) * 100, 2) AS variacao_pct,
    ROUND(
        AVG(valor) OVER (ORDER BY data ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
        4
    ) AS media_movel_7d,
    ROUND(
        AVG(valor) OVER (ORDER BY data ROWS BETWEEN 29 PRECEDING AND CURRENT ROW),
        4
    ) AS media_movel_30d
    -- TODO (Abner): acrescente aqui a coluna media_movel_30d.
FROM observacao
WHERE codigo_serie = 1;


-- IPCA do mês e acumulado em 12 meses, os dois em %.
-- O acumulado é composto: multiplica os 12 fatores (1 + taxa do mês). O SQL
-- não tem função de produto, então usa-se a soma dos logaritmos, porque
-- EXP(SUM(LN(x))) dá o mesmo resultado que multiplicar os x.
-- Os 11 primeiros meses ficam nulos, pois ainda não completam 12 meses.
CREATE VIEW vw_ipca_12m AS
SELECT
    data,
    valor AS ipca_mes,
    CASE
        WHEN COUNT(*) OVER ultimos_12_meses = 12
            THEN ROUND(
                (EXP(SUM(LN(1 + valor / 100)) OVER ultimos_12_meses) - 1) * 100,
                2
            )
    END AS ipca_12m
FROM observacao
WHERE codigo_serie = 433
WINDOW ultimos_12_meses AS (ORDER BY data ROWS BETWEEN 11 PRECEDING AND CURRENT ROW);


-- Juro real por mês, em % ao ano: a meta Selic do último dia do mês,
-- descontada do IPCA acumulado em 12 meses.
-- Fórmula: (1 + selic) / (1 + ipca_12m) - 1.
CREATE VIEW vw_juro_real_mensal AS
WITH selic_por_dia AS (
    SELECT
        CAST(DATE_TRUNC('month', data) AS DATE) AS mes,
        valor AS selic_meta,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('month', data)
            ORDER BY data DESC
        ) AS posicao
    FROM observacao
    WHERE codigo_serie = 432
)

SELECT
    ipca.data AS mes,
    selic.selic_meta,
    ipca.ipca_12m,
    ROUND(
        ((1 + selic.selic_meta / 100) / (1 + ipca.ipca_12m / 100) - 1) * 100,
        2
    ) AS juro_real
FROM vw_ipca_12m AS ipca
INNER JOIN selic_por_dia AS selic
    ON ipca.data = selic.mes
WHERE
    selic.posicao = 1
    AND ipca.ipca_12m IS NOT NULL;
