# GenForge

GenForge é uma plataforma integrada de bioinformática para genética vegetal, mutagênese EMS, análise de variantes, anotação, GWAS, seleção genômica e IA aplicada à genômica.

Esta primeira versão implementa a fundação da aplicação web e limita o escopo a autenticação, usuários, projetos, upload de VCF, ingestão inicial de variantes e consulta filtrada. GWAS, IA e seleção genômica entram apenas como interfaces para expansão futura.

## Arquitetura

O monorepo separa backend, frontend, documentação e infraestrutura:

```text
backend/
  app/
    core/
    auth/
    users/
    projects/
    samples/
    variants/
    annotation/
    reports/
    storage/
    tasks/
    gwas/
    ml/
    genomic_selection/
  alembic/
  tests/
frontend/
  src/
    api/
    modules/
      auth/
      projects/
      variants/
      dashboard/
      settings/
docs/
.github/workflows/
```

O backend usa FastAPI, SQLAlchemy 2.x, Pydantic v2, Alembic, PostgreSQL, Redis e Celery. Os módulos seguem uma divisão simples de Clean Architecture: modelos e entidades no domínio do módulo, serviços de aplicação, repositórios de infraestrutura e rotas HTTP como camada de entrada.

O frontend usa React, TypeScript, Vite, Material UI e Plotly. A interface inicial já possui login, projetos, upload de VCF, filtros de variantes, tabela e gráfico de distribuição.

## Escalabilidade de variantes

O fluxo de VCF foi desenhado para não processar arquivos grandes dentro da requisição HTTP:

1. A API salva o arquivo em storage local abstrato.
2. Registra `variant_files` e `variant_processing_jobs`.
3. Enfileira um job Celery.
4. O worker faz parsing streaming do VCF.
5. Variantes são inseridas em lotes.
6. Consultas são paginadas e usam índices compostos.

A tabela `variants` já inclui índice em `(project_id, chromosome, position)`, além de índices em `gene_id`, `impact` e `sample_id`. Para volumes maiores, o roadmap prevê particionamento por projeto/cromossomo, ingestão com `COPY`, tabelas de genótipos separadas e storage S3/MinIO.

## Requisitos

- Docker e Docker Compose
- Python 3.11+ para desenvolvimento local do backend
- Node.js 22.12+ para desenvolvimento local do frontend
- PostgreSQL 16
- Redis 7

Ferramentas de bioinformática previstas:

- bcftools
- samtools
- SnpEff
- Nextflow
- Primer3
- BioPython
- pysam
- cyvcf2

Na primeira versão, o parser VCF básico funciona sem depender de `cyvcf2`; os pacotes pesados ficam como extras opcionais.

Veja a lista completa de ferramentas externas e comandos de instalação em [docs/tools.md](docs/tools.md).

Arquivos de dependências Python:

- `requirements.txt`: atalho na raiz para instalar o backend mínimo.
- `backend/requirements.txt`: dependências runtime da API.
- `backend/requirements-dev.txt`: runtime, testes e lint.
- `backend/requirements-bio.txt`: runtime e bibliotecas Python de bioinformática.
- `backend/requirements-ml.txt`: runtime e bibliotecas de machine learning.

## Execução com Docker

Copie o arquivo de ambiente se quiser customizar variáveis:

```powershell
Copy-Item .env.example .env
```

Suba os serviços:

```powershell
docker compose up --build
```

Em outro terminal, aplique a migração inicial:

```powershell
docker compose exec backend alembic upgrade head
```

Serviços:

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>
- Frontend: <http://localhost:5173>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Desenvolvimento local do backend

No Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

No Linux/macOS:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Extras de bioinformática e IA:

```bash
python -m pip install -r requirements-bio.txt
python -m pip install -r requirements-ml.txt
```

## Desenvolvimento local do frontend

```bash
cd frontend
npm install
npm run dev
```

Para build:

```bash
npm run build
```

## Testes

Backend:

```bash
cd backend
pytest
ruff check .
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Teste em servidor Linux

Para testar o GenForge em um servidor acessado por VPN ou IP externo, configure `backend/.env` e `frontend/.env` antes de iniciar os servicos.

- Backend: definir `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` e `CORS_ORIGINS`.
- Frontend: definir `VITE_API_BASE_URL`, por exemplo `http://200.235.143.10:8000`.
- API: rodar `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Frontend: rodar `npm run dev -- --host 0.0.0.0` ou validar com `npm run build`.

Veja o passo a passo em [docs/server-deploy.md](docs/server-deploy.md).

## Endpoints principais

- `GET /`
- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/variants/upload?project_id={uuid}`
- `GET /api/v1/variants?project_id={uuid}&chromosome=Chr1&gene_id=Gene001&limit=25&offset=0`
- `GET /api/v1/variants/files?project_id={uuid}`
- `GET /api/v1/variants/jobs?project_id={uuid}`
- `GET /api/v1/variants/jobs/{job_id}`

## Modelo inicial

Entidades principais:

- `User`: autenticação e ownership.
- `Project`: unidade de trabalho.
- `Sample`: amostra vinculada ao projeto.
- `Gene`: gene anotado por `gene_id` e cromossomo.
- `Variant`: variante consultável por projeto, cromossomo, posição, gene e impacto.
- `VariantFile`: arquivo VCF armazenado.
- `VariantProcessingJob`: rastreabilidade da ingestão.

Campos mínimos solicitados:

- `Gene`: `id`, `gene_id`, `chromosome`
- `Variant`: `id`, `chromosome`, `position`, `reference`, `alternative`, `impact`, `gene_id`
- `Sample`: `id`, `sample_name`
- `Project`: `id`, `project_name`

## Próximos passos

O roadmap técnico completo está em [docs/ROADMAP.md](docs/ROADMAP.md). A documentação arquitetural está em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). O estado implementado, validações e pendências ficam em [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md).
