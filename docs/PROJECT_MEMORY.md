# Project Memory

## 2026-07-07 - Auth access error handling

### Implementado

- Falhas SQLAlchemy durante requisicoes agora sao convertidas para HTTP 503 com mensagem clara sobre `DATABASE_URL`, `backend/.env`, credenciais PostgreSQL e `alembic upgrade head`.
- Frontend preserva mensagens 503 da API para que cadastro/login mostrem erro acionavel em vez de falha generica.
- Documentacao de deploy e `.env.example` reforcam que senhas PostgreSQL com caracteres especiais precisam ser URL-encoded, por exemplo `@` como `%40`.

### Causa raiz observada

- O log do servidor em `erros.txt` mostra `FATAL: autenticacao do tipo senha falhou para o usuario "genforge"` ao rodar `alembic upgrade head`.
- Isso indica que o PostgreSQL respondeu, mas usuario/senha em `DATABASE_URL` nao conferem ou a senha nao foi codificada corretamente.

### Validacoes esperadas

- `cd backend && pytest`
- `cd backend && ruff check .`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## 2026-06-26 - Phase 1 MVP consolidation

### Implementado

- Backend Phase 1 consolidado para `auth`, `users`, `projects`, `storage`, `samples` e `variants`.
- `Project` agora possui CRUD completo: criar, listar, detalhar, editar e excluir com ownership por usuario.
- Tabelas principais da Fase 1 receberam `updated_at` por migration Alembic.
- API de variantes expoe historico paginado de arquivos VCF e jobs de processamento.
- Upload VCF continua salvando arquivos em `storage_data/projects/{project_id}/` e registrando metadados no PostgreSQL.
- `STORAGE_DIR` padrao foi alinhado para gerar `storage_data/projects/{project_id}` em execucao local e `/data/genforge/projects/{project_id}` no Docker Compose.
- Frontend usa `VITE_API_BASE_URL`, permite CRUD de projetos, upload VCF, paginacao de variantes e exibicao de arquivos/jobs.
- Script `frontend npm run lint` foi restringido a `src` para nao varrer `dist` gerado pelo build.

### Arquivos e modulos impactados

- Backend: `projects`, `users`, `samples`, `variants`, `storage`, `alembic` e `tests`.
- Frontend: `src/api/client.ts`, `src/modules/projects/ProjectsPage.tsx`, `src/modules/variants/VariantsPage.tsx` e `package.json`.
- Documentacao: `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/api.md` e este arquivo.

### Validacoes executadas

- `cd backend && py -3 -m ruff check .` passou.
- `cd backend && py -3 -m pytest` passou com 12 testes.
- `cd frontend && npm.cmd install` passou; houve aviso `allow-scripts` para revisar scripts de instalacao de `es5-ext`.
- `cd frontend && npm.cmd run build` passou.
- `cd frontend && npm.cmd run build` emitiu aviso nao bloqueante de chunk maior que 500 kB.
- `cd frontend && npm.cmd run lint` passou.

### Validacao bloqueada

- Comando: `cd backend && py -3 -m alembic upgrade head --sql`
- Erro: `Unable to create process using '...Python314\\python.exe -m alembic upgrade head --sql': Acesso negado.`
- Possivel causa: bloqueio local do launcher Python no ambiente Windows usado pelo Codex.
- Arquivo relacionado: `backend/alembic/versions/202606260001_add_updated_at_to_phase1_tables.py`.

### Pendencias

- Validar `alembic upgrade head` no servidor Linux com o ambiente Python real.
- Validar worker Celery e Redis processando `variants.process_variant_file` com um VCF pequeno.
- Adicionar logs basicos da aplicacao.
- Cobrir filtros de variantes com testes automatizados.
- Decidir quando trocar storage local por MinIO/S3.
