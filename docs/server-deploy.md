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
STORAGE_DIR=storage_data/uploads
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://200.235.143.10:5173
```

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
