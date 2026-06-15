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

## Definição de Conclusão

Uma tarefa só é considerada concluída se:

* código compilar
* testes passarem
* documentação for atualizada
* migrations forem criadas quando necessário
* frontend e backend continuarem funcionando
