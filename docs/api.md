# API Inicial

Base URL local:

```text
http://localhost:8000/api/v1
```

## Autenticação

```http
POST /auth/register
POST /auth/login
```

O login retorna token JWT Bearer. Use:

```http
Authorization: Bearer <token>
```

## Projetos

```http
GET /projects
POST /projects
GET /projects/{project_id}
PATCH /projects/{project_id}
DELETE /projects/{project_id}
```

`DELETE /projects/{project_id}` retorna `204 No Content`.

## Variantes

```http
POST /variants/upload?project_id=<uuid>
GET /variants?project_id=<uuid>&chromosome=Chr1&gene_id=Gene001&impact=MODERATE&start=1&end=100000&limit=25&offset=0
GET /variants/files?project_id=<uuid>&limit=10&offset=0
GET /variants/jobs?project_id=<uuid>&status=queued&limit=10&offset=0
GET /variants/jobs/{job_id}
```

O upload retorna `202 Accepted` com `VariantFile` e `VariantProcessingJob`.

As respostas paginadas usam o formato:

```json
{
  "items": [],
  "total": 0,
  "limit": 25,
  "offset": 0
}
```
