Você é um arquiteto de software sênior especializado em Bioinformática, IA e sistemas distribuídos.

Seu objetivo é iniciar o desenvolvimento de uma plataforma chamada BioStack.

# VISÃO DO PRODUTO

BioStack é uma plataforma integrada de bioinformática voltada para genética vegetal, mutagênese EMS, análise de variantes, GWAS, seleção genômica e inteligência artificial aplicada à genômica.

A plataforma deverá funcionar inicialmente como uma aplicação web moderna, mas toda a arquitetura deve permitir futuras interfaces CLI e Desktop sem duplicação de código.

O projeto deverá seguir princípios de Clean Architecture, Domain Driven Design (DDD) e desenvolvimento modular.

---

# STACK TECNOLÓGICA

Backend:
- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Redis
- Celery

Frontend:
- React
- TypeScript
- Vite
- Material UI
- Plotly

Bioinformática:
- bcftools
- samtools
- SnpEff
- Nextflow
- Primer3
- BioPython
- pysam
- cyvcf2

Machine Learning:
- Scikit-learn
- XGBoost
- LightGBM
- PyTorch

Infraestrutura:
- Docker
- Docker Compose
- GitHub Actions

---

# OBJETIVO DA PRIMEIRA VERSÃO

Implementar apenas:

1. Sistema de autenticação
2. Gestão de usuários
3. Gestão de projetos
4. Upload de arquivos VCF
5. Pipeline de anotação de variantes
6. Banco de dados de variantes
7. Interface para consulta e filtragem

Não implementar GWAS, IA ou seleção genômica nesta primeira etapa.

Esses módulos devem apenas possuir interfaces vazias para expansão futura.

---

# ESTRUTURA MODULAR

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

frontend/

    src/

        modules/

            auth/

            projects/

            variants/

            dashboard/

            settings/

---

# MÓDULO VARIANTS

O módulo variants será o núcleo inicial.

Deve permitir:

- Upload de VCF
- Armazenamento do arquivo
- Registro do processamento
- Execução futura de SnpEff
- Armazenamento das variantes

Modelo mínimo:

Gene
Variant
Sample
Project

Campos mínimos:

Gene:
- id
- gene_id
- chromosome

Variant:
- id
- chromosome
- position
- reference
- alternative
- impact
- gene_id

Sample:
- id
- sample_name

Project:
- id
- project_name

---

# REQUISITOS DE QUALIDADE

- Tipagem completa
- Pydantic v2
- Testes automatizados
- Estrutura pronta para CI/CD
- Arquitetura desacoplada
- Serviços separados
- API REST documentada

---

# TAREFA

1. Criar toda a estrutura inicial do monorepo.
2. Gerar a árvore completa de diretórios.
3. Criar os arquivos base.
4. Criar modelos iniciais SQLAlchemy.
5. Criar autenticação JWT.
6. Criar migrations Alembic.
7. Criar Docker Compose.
8. Criar README detalhado.
9. Criar documentação arquitetural.
10. Criar roadmap técnico para as próximas versões.

Antes de gerar código:

- explique a arquitetura proposta;
- identifique possíveis gargalos futuros;
- proponha melhorias;
- somente depois gere os arquivos.

Sempre priorize escalabilidade para milhões de variantes genômicas.