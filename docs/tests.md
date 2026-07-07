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

## Ultima validacao registrada

Data: 2026-07-07.

- `cd backend && py -3 -m pytest`: passou com 25 testes.
- `cd backend && py -3 -m ruff check .`: passou.
- Alembic offline `upgrade head --sql`: passou.
- Alembic online `upgrade head` com `localhost:5432/genforge`: bloqueado por
  timeout de conexao ao PostgreSQL local.
- `docker compose up -d postgres`: bloqueado porque `docker` nao esta no PATH.
- `cd frontend && npm.cmd run build`: passou com aviso nao bloqueante de chunk
  maior que 500 kB.
