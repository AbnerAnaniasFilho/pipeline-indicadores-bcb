# Pipeline de indicadores econômicos (Banco Central)

Projeto de portfólio para vaga de Engenheiro de Dados Júnior. O pipeline extrai séries da API pública do Banco Central (SGS), carrega em PostgreSQL com carga incremental, expõe views analíticas em SQL e alimenta um dashboard em Power BI.

## Como quero trabalhar

- Sou estudante de ADS e estou aprendendo engenharia de dados. Este projeto vai para o meu GitHub, e preciso conseguir explicar cada linha numa entrevista.
- Faça uma etapa do roteiro por vez. Antes de escrever código, explique em poucas linhas o que vai fazer e por quê. No fim de cada etapa, pare e espere eu testar e confirmar.
- Quando aparecer um conceito novo para mim (SQLAlchemy, upsert, carga incremental, logging, retries), explique com um exemplo curto antes de usar.
- De vez em quando, proponha que eu mesmo escreva uma função pequena e depois revise o meu código, em vez de escrever tudo.
- Prefira código simples e legível a soluções espertas. Não adicione dependências fora da lista abaixo sem me perguntar.
- Responda em português.

## Ambiente

- Windows, terminal PowerShell. Dê comandos para Windows.
- Python 3.12 num ambiente conda chamado `indicadores-bcb` (uso Anaconda). Mantenha o `requirements.txt` atualizado.
- PostgreSQL instalado localmente. Credenciais só no `.env`.
- Power BI Desktop: o dashboard eu monto manualmente. Seu papel é preparar as views e tirar dúvidas.

## Fonte de dados: API SGS do Banco Central

- Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial=DD/MM/AAAA&dataFinal=DD/MM/AAAA`
- Pública, sem chave de API.
- Desde 26/03/2025 as consultas em JSON exigem `dataInicial` e `dataFinal`, e o intervalo máximo é de 10 anos. Busque em janelas de no máximo 3 anos, que é mais seguro.
- A resposta é uma lista de objetos `{"data": "dd/mm/aaaa", "valor": "..."}`, com os dois campos como texto. Converta para `date` e número.
- Histórico inicial: a partir de 01/01/2015.

| Código | Série | Periodicidade | Unidade |
|---|---|---|---|
| 1 | Dólar comercial (venda) | diária, dias úteis | R$ |
| 432 | Meta Selic definida pelo Copom | diária | % a.a. |
| 433 | IPCA | mensal | % no mês |

## Estrutura do projeto

```
pipeline-indicadores-bcb/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .env.example        # chaves sem valores
├── .gitignore          # inclui .env, logs/, __pycache__/
├── src/
│   ├── config.py       # lê o .env e a lista de séries
│   ├── extract.py      # chama a API em janelas de datas
│   ├── load.py         # grava no PostgreSQL com upsert
│   └── pipeline.py     # orquestra as séries; roda com: python -m src.pipeline
├── sql/
│   ├── 01_schema.sql   # tabelas
│   └── 02_views.sql    # views analíticas
├── tests/              # pytest, sem chamar a API de verdade
├── dashboard/          # arquivo .pbix e prints
└── docs/               # diagrama da arquitetura
```

Dependências: `requests`, `pandas`, `SQLAlchemy`, `psycopg[binary]`, `python-dotenv`, `pytest`.

## Modelo de dados

Nomes de tabelas, colunas e funções em português, sem acento, em snake_case.

- `serie`: `codigo` (PK), `nome`, `unidade`, `periodicidade`
- `observacao`: `codigo_serie` (FK), `data`, `valor` (NUMERIC), `carregado_em` (TIMESTAMP, padrão now()). Chave primária: (`codigo_serie`, `data`).

## Regras técnicas

- Carga incremental: para cada série, consultar a maior data já salva. Se não houver nenhuma, começar em 01/01/2015. Buscar do dia seguinte até hoje.
- Idempotência: `INSERT ... ON CONFLICT (codigo_serie, data) DO UPDATE`. Rodar o pipeline duas vezes não pode duplicar dados.
- Erros de rede: timeout nas requisições e até 3 tentativas com espera crescente. Se uma série falhar, registrar o erro e seguir com as outras.
- Logging com o módulo `logging`, no console e em `logs/pipeline.log`. Nada de `print`.
- Nunca commitar o `.env` nem credenciais.
- Testes com pytest para as funções puras: geração das janelas de datas e conversão da resposta da API.

## Views analíticas (sql/02_views.sql)

- `vw_dolar_diario`: cotação, variação % contra o dia anterior (LAG) e médias móveis de 7 e 30 dias (window functions).
- `vw_ipca_12m`: IPCA mensal e acumulado em 12 meses (composto, não soma simples).
- `vw_juro_real_mensal`: meta Selic do último dia de cada mês contra o IPCA acumulado em 12 meses, com o juro real calculado por `(1 + selic) / (1 + ipca_12m) - 1`.

## Roteiro

1. Setup: ambiente conda, `requirements.txt`, `.gitignore`, `.env.example` e um teste de conexão com o PostgreSQL.
2. Extração de uma série com janelas de datas, mais os testes.
3. Schema (`sql/01_schema.sql`) e carga com upsert.
4. Pipeline incremental para as 3 séries, com logging e retries.
5. Views analíticas.
6. Dashboard no Power BI (eu faço).
7. README final: problema, diagrama da arquitetura, como rodar, decisões técnicas e prints do dashboard.

## Git

- Um commit por etapa concluída. Sugira a mensagem e pergunte antes de commitar.
- Conventional Commits em português e em minúsculas, por exemplo `feat: adiciona extração da api do bcb`, `test: cobre geração de janelas de datas`, `docs: descreve arquitetura no readme`.

## Pronto quando

- `python -m src.pipeline` roda do zero e roda de novo sem duplicar dados.
- Os testes passam.
- Outra pessoa consegue rodar o projeto seguindo só o README.
