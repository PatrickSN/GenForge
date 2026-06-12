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
```

## Variantes

```http
POST /variants/upload?project_id=<uuid>
GET /variants?project_id=<uuid>&chromosome=Chr1&gene_id=Gene001&impact=MODERATE&start=1&end=100000
```

O upload retorna `202 Accepted` com `VariantFile` e `VariantProcessingJob`.
