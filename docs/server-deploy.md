# Teste em servidor Linux

Este guia prepara o GenForge para testes manuais em um servidor Linux acessado por VPN ou IP externo. Nao commite arquivos `.env` reais.

## Backend

1. Crie o arquivo de ambiente:

```bash
cd backend
cp .env.example .env
```

2. Edite `backend/.env`:

```dotenv
APP_ENV=development
SECRET_KEY=troque-por-uma-chave-local-com-mais-de-16-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/genforge
REDIS_URL=redis://localhost:6379/0
STORAGE_DIR=storage_data
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://200.235.143.10:5173
```

O valor de `DATABASE_URL` deve usar o usuario e a senha reais do PostgreSQL no servidor.
Se a senha tiver caracteres especiais como `@`, `#`, `/` ou `:`, codifique a senha para URL antes de colocar no arquivo `.env`.
Exemplo: uma senha no formato `abc@123` deve entrar na URL como `abc%40123`.
Erro como `FATAL: autenticacao do tipo senha falhou para o usuario "genforge"` indica que o PostgreSQL respondeu, mas o usuario ou a senha em `DATABASE_URL` nao conferem com o banco.

Use `localhost` quando o backend roda diretamente no servidor e acessa um PostgreSQL local. Use `postgres` como host apenas quando o backend roda dentro do Docker Compose deste repositorio.

Antes de rodar as migrations, valide o login no PostgreSQL sem colocar a senha no historico do shell:

```bash
psql "postgresql://usuario@localhost:5432/genforge" -W -c "select 1;"
```

Se esse comando falhar, corrija primeiro a senha do usuario PostgreSQL ou o valor de `DATABASE_URL`; cadastro e login da aplicacao dependem desse acesso ao banco.

3. Instale dependencias e aplique migrations:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
alembic upgrade head
```

4. Rode a API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Teste os endpoints:

```bash
curl http://200.235.143.10:8000/health
curl http://200.235.143.10:8000/
```

Abra `http://200.235.143.10:8000/docs` no navegador. O endpoint `/` deve retornar uma mensagem simples da API; se `/health` funcionar, a API esta ativa.

## Frontend

1. Crie o arquivo de ambiente:

```bash
cd frontend
cp .env.example .env
```

2. Edite `frontend/.env` para apontar ao backend do servidor:

```dotenv
VITE_API_BASE_URL=http://200.235.143.10:8000
```

3. Instale dependencias e rode o Vite acessivel na rede:

```bash
npm install
npm run dev -- --host 0.0.0.0
```

Para validar o build:

```bash
npm run lint
npm run build
```

## Login

Com o backend e o frontend ativos, acesse `http://200.235.143.10:5173`, use "Criar acesso" para registrar um usuario inicial e depois faca login.

Tambem e possivel testar pela API:

```bash
curl -X POST http://200.235.143.10:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@genforge.local","full_name":"GenForge Admin","password":"genforge123"}'

curl -X POST http://200.235.143.10:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@genforge.local","password":"genforge123"}'
```

Se o frontend mostrar erro de conexao, confirme se o backend esta ativo e se `VITE_API_BASE_URL` aponta para o host e porta corretos.

## Smoke manual da Fase 1

Depois do login pelo frontend:

1. Crie um projeto em `Projetos`.
2. Edite a descricao do projeto e salve.
3. Abra os detalhes do projeto.
4. Acesse `Variantes`, selecione o projeto e envie um arquivo `.vcf` pequeno.
5. Verifique se a tela mostra o arquivo em `Arquivos VCF`, o job em `Jobs` e a tabela paginada de variantes.

No servidor Linux, valide tambem:

```bash
cd backend
alembic upgrade head
pytest
ruff check .
```

Se `alembic upgrade head` falhar por conexao ou autenticacao, revise `DATABASE_URL` em `backend/.env` e confirme o acesso com `psql`.
