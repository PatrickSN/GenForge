# AGENTS.md

## Projeto

GenForge é uma plataforma integrada de bioinformática para:

* Análise de Variantes
* Banco de Mutantes EMS
* GWAS
* Seleção Genômica
* Inteligência Artificial aplicada à Genômica
* Pipelines NGS

---

## Objetivo Atual

Estamos implementando a Fase 1.

Módulos permitidos:

* auth
* users
* projects
* files
* storage
* variants

Não implementar:

* GWAS
* EMS
* IA
* Primer Design
* NGS

Esses módulos devem permanecer apenas como placeholders.

---

## Stack Oficial

Backend:

* Python 3.11+
* FastAPI
* SQLAlchemy 2.x
* PostgreSQL
* Alembic

Frontend:

* React
* TypeScript
* Vite
* Material UI

Infraestrutura:

* Docker
* Redis
* Celery

---

## Arquitetura

Utilizar arquitetura modular.

Cada módulo deve possuir:

* models.py
* schemas.py
* repository.py
* service.py
* router.py

Routers não devem conter regra de negócio.

Toda regra deve ficar em services.

Acesso ao banco deve ficar em repositories.

---

## Banco de Dados

Usar UUID como chave primária.

Sempre incluir:

* created_at
* updated_at

Evitar chaves inteiras autoincrementais.

---

## Upload de Arquivos

Armazenar arquivos em:

storage_data/projects/{project_id}/

Não armazenar arquivos binários no PostgreSQL.

Armazenar apenas metadados.

---

## Segurança

Autenticação JWT obrigatória.

Senhas devem ser armazenadas com bcrypt.

Nunca armazenar senhas em texto puro.

---

## Testes

Toda funcionalidade nova deve possuir testes.

Cobertura mínima:

* autenticação
* projetos
* upload de arquivos

Comandos de validacao atuais:

Backend:

```powershell
cd backend
py -3 -m pytest
py -3 -m ruff check .
```

Alembic em banco local de desenvolvimento:

```powershell
cd backend
$env:GENFORGE_APP_ENV = "development"
$env:GENFORGE_DATABASE_URL = "postgresql+psycopg://genforge:genforge@localhost:5432/genforge?connect_timeout=5"
$env:GENFORGE_SECRET_KEY = "change-this-secret-key-for-local-development"
py -3 -m alembic upgrade head
```

Frontend:

```powershell
cd frontend
npm.cmd run build
```

Detalhes e status das ultimas validacoes ficam em `docs/tests.md`.

---

## Roadmap

Fase 1:

* usuários
* projetos
* arquivos
* upload de VCF
* ingestão inicial de variantes
* consulta paginada de variantes

Fase 2:

* variantes
* parser VCF
* filtros

Fase 3:

* banco EMS

Fase 4:

* primers

Fase 5:

* GWAS

Fase 6:

* seleção genômica

Fase 7:

* IA

Fase 8:

* pipelines NGS

---

## Regras para Agentes

Antes de alterar código:

1. Ler README.md
2. Ler AGENTS.md
3. Ler a estrutura do módulo relacionado

Não criar novos padrões arquiteturais.

Não mover arquivos sem necessidade.

Não alterar módulos não relacionados à tarefa.

Não adicionar dependências sem justificativa.

Sempre manter compatibilidade com PostgreSQL.

Sempre manter compatibilidade com Docker Compose.

---

## Regras de Deploy e Git

Nao commitar secrets, arquivos `.env` reais, tokens, chaves privadas ou senhas.

Nao alterar `main` diretamente. Criar uma branch curta com prefixo `codex/` para mudancas de agente.

Rodar os testes e validacoes disponiveis antes de finalizar. Quando uma validacao falhar por dependencia externa, documentar o comando, o erro, a causa provavel e o arquivo relacionado.

Preservar compatibilidade com servidor Linux, Docker Compose, PostgreSQL e execucao via `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

Preferir mudancas pequenas, revisaveis e alinhadas aos padroes existentes do repositorio.

---

## Memoria do Projeto

Atualizar `docs/PROJECT_MEMORY.md` quando uma tarefa alterar comportamento, contratos de API, fluxo de execucao, validacoes ou pendencias relevantes.

Registrar sempre:

* data da alteracao
* resumo do que foi implementado
* arquivos ou modulos impactados
* comandos de validacao executados
* falhas conhecidas e proximos passos

Estado atual da Fase 1 em 2026-06-26:

* backend possui auth, users, projects, storage e variants funcionais para smoke manual
* projetos possuem CRUD completo com ownership por usuario
* upload VCF registra arquivo e job; ingestao completa depende do worker Celery
* frontend usa `VITE_API_BASE_URL`, gerencia projetos, envia VCF e exibe variantes paginadas, arquivos e jobs
* ainda falta validar migrations e worker Celery no servidor Linux real antes de encerrar a Fase 1

---

## Definição de Conclusão

Uma tarefa só é considerada concluída se:

* código compilar
* testes passarem
* documentação for atualizada
* migrations forem criadas quando necessário
* frontend e backend continuarem funcionando
