# Testes e validacoes

Este documento registra os comandos de validacao da Fase 1. Nao use banco de
producao para testes locais ou migrations de verificacao.

## Backend

Execute a partir de `backend/`:

```powershell
py -3 -m pytest
py -3 -m ruff check .
```

A camada inicial de pytest usa fixtures centralizadas em `backend/tests/conftest.py`
e helpers em `backend/tests/helpers.py` para:

- banco SQLite temporario por teste;
- usuario cadastrado;
- cabecalho de autenticacao JWT;
- projeto do usuario autenticado;
- arquivo VCF minimo;
- captura do enfileiramento Celery sem executar worker real.

Cobertura atual:

- `auth`: cadastro, login, rejeicao de email duplicado e senha invalida.
- `users`: `/users/me`, protecao por token e listagem paginada.
- `projects`: CRUD, paginacao e isolamento por owner.
- `variants`: upload VCF, rejeicao de extensao invalida, arquivos/jobs, listagem
  paginada de variantes e filtros implementados por cromossomo, gene, impacto e
  intervalo de posicao.
- `alembic`: arvore de revisions com head unico.

## Alembic com banco de desenvolvimento

Para validar migrations contra PostgreSQL local de desenvolvimento:

```powershell
cd backend
$env:GENFORGE_APP_ENV = "development"
$env:GENFORGE_DATABASE_URL = "postgresql+psycopg://genforge:genforge@localhost:5432/genforge?connect_timeout=5"
$env:GENFORGE_SECRET_KEY = "change-this-secret-key-for-local-development"
py -3 -m alembic upgrade head
```

Se o launcher `py` falhar no Windows, use o executavel Python do ambiente virtual
do backend e rode o mesmo `-m alembic upgrade head`.

Validacao offline dos scripts, sem conectar ao banco:

```powershell
cd backend
$env:GENFORGE_APP_ENV = "development"
$env:GENFORGE_DATABASE_URL = "postgresql+psycopg://genforge:genforge@localhost:5432/genforge"
$env:GENFORGE_SECRET_KEY = "change-this-secret-key-for-local-development"
python -m alembic upgrade head --sql
```

## Frontend

Execute a partir de `frontend/`:

```powershell
npm.cmd run build
```

No Linux/macOS, `npm run build` e equivalente.

## Smoke da API em servidor Linux

Com a API ativa:

```bash
cd backend
python -m scripts.smoke_phase1 --base-url http://127.0.0.1:8000
```

Use `--cleanup-project` para tentar remover o projeto criado pelo smoke ao final:

```bash
cd backend
python -m scripts.smoke_phase1 --base-url http://127.0.0.1:8000 --cleanup-project
```

Com Redis e worker Celery ativos, exigindo ingestao completa do VCF:

```bash
cd backend
python -m scripts.smoke_phase1 --base-url http://127.0.0.1:8000 --require-worker
```

O script valida `/`, `/health`, cadastro, login, `/users/me`, criacao de projeto,
upload VCF, listagem de arquivos, jobs e variantes. Com `--require-worker`, ele
polls o job ate `finished` e falha se nenhuma variante for persistida.

## Ultima validacao registrada

Data: 2026-07-07.

- `cd backend && py -3 -m pytest`: passou com 30 testes.
- `cd backend && py -3 -m ruff check .`: passou.
- Alembic offline `upgrade head --sql`: passou.
- Alembic online no servidor Linux: `python3.11 -m alembic current`, `heads`,
  `history` e `upgrade head` chegaram em `202606260001 (head)`.
- Backup no servidor via `pg_dump "$DATABASE_URL"` falhou porque `DATABASE_URL`
  nao estava exportado no shell e o `pg_dump` tentou usar o usuario Linux.
- `celery -A app.tasks.celery_app inspect ping` no servidor retornou `No nodes
  replied within time constraint`; worker/Redis real ainda precisa ser validado.
- `python -m scripts.smoke_phase1 --base-url http://127.0.0.1:8000` passou
  contra a API local ativa para auth, users, projects, upload VCF e listagens.
- `python -m scripts.smoke_phase1 --require-worker --wait-job-seconds 3`
  confirmou falha controlada quando o job permanece `queued` sem worker.
- `--cleanup-project` contra o processo ativo em `127.0.0.1:8000` retornou 503;
  a correcao de cascade foi adicionada e validada por teste, mas o backend ativo
  precisa ser reiniciado para carregar a nova versao.
- `cd frontend && npm.cmd run build`: passou com aviso nao bloqueante de chunk
  maior que 500 kB.
