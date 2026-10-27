# insights

Plataforma multi-tenant que coleta dados de CRMs e ERPs via API, organiza esses dados em um warehouse e gera **insights automáticos** — métricas, variações relevantes e explicações em linguagem natural — entregues aos clientes por dashboard e notificações.

> **Status:** estágio inicial. A estrutura do monorepo, a infraestrutura local (Postgres + Redis) e o modelo de permissões do banco já estão definidos; os pacotes ainda são esqueletos.

---

## Visão geral

```
 CRMs / ERPs ──► connectors ──► warehouse (raw) ──► dbt ──► semantic ──► insights ──► narrator ──► notifier
                     ▲                                                      │
                     └──────────────── orchestrator (agendamento) ──────────┘
                                                                            │
                                                     api ◄──────────────────┘ ──► web
```

O sistema é dividido em dois planos, cada um com seu próprio banco Postgres:

| Plano | Banco | Conteúdo |
|---|---|---|
| **Control plane** | `app` | Tenants, usuários, credenciais de conectores, configurações, insights gerados |
| **Data plane** | `warehouse` | Dados extraídos das fontes e modelos transformados pelo dbt |

O isolamento entre clientes é feito com **Row-Level Security (RLS)** do Postgres.

---

## Estrutura do repositório

```
.
├── apps/
│   ├── api/                  # API HTTP (control plane)
│   └── web/                  # Frontend
├── packages/
│   ├── core/                 # Modelos de domínio, config e utilitários compartilhados
│   ├── connectors/           # Integrações com CRMs/ERPs (extração via API)
│   ├── semantic/             # Camada semântica: definição de métricas e dimensões
│   ├── insights/             # Detecção de insights (variações, anomalias, tendências)
│   ├── narrator/             # Transforma insights em texto em linguagem natural
│   └── notifier/             # Entrega de insights (e-mail, mensagens, etc.)
├── pipelines/
│   └── orchestrator/         # Orquestração dos pipelines (Dagster)
├── transform/
│   └── dbt/                  # Modelos de transformação do warehouse
├── metric_packs/             # Pacotes de métricas por tipo de negócio/fonte
├── infra/
│   ├── docker/postgres/init/ # Scripts executados na criação do Postgres
│   └── sql/                  # SQL de infraestrutura
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── conectores/           # Documentação de cada conector
│   └── runbooks/             # Procedimentos operacionais
├── docker-compose.yml
└── pyproject.toml            # Raiz do workspace uv
```

---

## Stack

- **Python 3.12** com workspace do [uv](https://docs.astral.sh/uv/) (`apps/api`, `packages/*`, `pipelines/*`)
- **PostgreSQL 17** — bancos `app` e `warehouse`
- **Redis 7** — filas e cache
- **dbt** — transformações no warehouse
- **Dagster** — orquestração
- **Alembic** — migrations do banco `app`
- **pytest** e **ruff** — testes e lint

---

## Como rodar localmente

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker e Docker Compose

### 1. Subir a infraestrutura

```bash
docker compose up -d
```

| Serviço | Porta no host |
|---|---|
| Postgres | `5438` |
| Redis | `6380` |

Na primeira inicialização, o script `infra/docker/postgres/init/01-init.sql` cria os bancos e os roles. Ele só roda com o volume vazio — para reaplicá-lo, use `docker compose down -v` (apaga os dados).

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Valores para o ambiente local:

```env
APP_DATABASE_URL=postgresql://app:app@localhost:5438/app
APP_MIGRATOR_DATABASE_URL=postgresql://migrator:migrator@localhost:5438/app
WAREHOUSE_DATABASE_URL=postgresql://migrator:migrator@localhost:5438/warehouse
REDIS_URL=redis://localhost:6380/0
```

> As senhas acima são apenas para desenvolvimento.

### 3. Instalar dependências

```bash
uv sync
```

### 4. Testes e lint

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

---

## Modelo de acesso ao banco

| Role | Uso | Observações |
|---|---|---|
| `migrator` | Alembic e dbt | Dono dos bancos e das tabelas |
| `app` | API e jobs | `NOBYPASSRLS` — sempre sujeito às policies de RLS |

Toda tabela criada pelo `migrator` no schema `public` do banco `app` já concede `SELECT/INSERT/UPDATE/DELETE` ao role `app`, sem grants manuais por migration.

---

## Convenções

- **Idioma do código:** nomes de tabelas, colunas, valores, identificadores e código em **inglês**. Documentação pode ser em português.
- **Autenticação:** todo usuário tem senha (`password_hash` obrigatório); não há login exclusivamente por provedor externo.
- **Decisões de arquitetura** são registradas em `docs/adr/`.
- **Segredos** ficam no `.env`, nunca no repositório (só o `.env.example` é versionado).
