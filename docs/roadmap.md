# Roadmap Técnico

## Versão 0.1 - Fundação e variantes

Escopo atual:

- Monorepo backend/frontend.
- FastAPI com OpenAPI.
- Autenticação JWT.
- Gestão inicial de usuários.
- Gestão de projetos.
- Upload de VCF.
- Storage local abstrato.
- Registro de jobs de processamento.
- Worker Celery para ingestão.
- Parser VCF inicial com suporte a `ANN` do SnpEff.
- Modelos SQLAlchemy e migração Alembic.
- Consulta filtrada e paginada de variantes.
- Frontend React com login, projetos, upload, filtros, tabela e Plotly.
- Docker Compose.
- CI inicial.

## Versão 0.2 - Robustez de ingestão

- Idempotência por checksum de arquivo.
- Staging tables para VCF.
- Inserção PostgreSQL com `COPY`.
- Validação estrutural de VCF com `bcftools`.
- Suporte multi-sample real com tabela de genótipos.
- Job status em tempo real via polling ou WebSocket.
- Retentativas controladas e logs estruturados por job.
- Testes de integração com PostgreSQL e Redis.

## Versão 0.3 - Anotação SnpEff

- Implementar porta `VariantAnnotator`.
- Integrar SnpEff local.
- Registrar versão do banco de anotação.
- Persistir consequência, transcript, effect, HGVS e impacto.
- Permitir reanotação controlada por versão.
- Executar anotação em fila separada.

## Versão 0.4 - Escala de banco

- Particionamento de `variants`.
- Índices BRIN para posições.
- Materialized views para agregações por projeto/gene/impacto.
- Filtros por região genômica com API dedicada.
- Export assíncrono de resultados.
- Estratégia de arquivamento para VCF bruto e artefatos.

## Versão 0.5 - Pipelines Nextflow

- Orquestrar workflows com Nextflow.
- Integrar bcftools, samtools e SnpEff.
- Rastrear parâmetros, versão de ferramentas e outputs.
- Adicionar auditoria por projeto.
- Preparar execução local, HPC e cloud.

## Versão 0.6 - Relatórios

- Relatórios por projeto.
- Sumários por cromossomo, gene e impacto.
- Exportação CSV/XLSX/Parquet.
- Geração assíncrona de artefatos.
- Visualizações adicionais no frontend.

## Versão 0.7 - GWAS

- Interfaces para fenótipos e covariáveis.
- Controle de qualidade de marcadores.
- Integração com pipelines GWAS.
- Manhattan plot e QQ plot.
- Armazenamento de resultados por experimento.

## Versão 0.8 - Seleção genômica

- Matrizes genômicas.
- Treinamento de modelos de predição.
- Validação cruzada.
- Ranking de candidatos.
- Relatórios de acurácia e importância de marcadores.

## Versão 0.9 - IA aplicada

- Pipelines Scikit-learn, XGBoost, LightGBM e PyTorch.
- Feature store genômica.
- Versionamento de modelos.
- Avaliação reprodutível.
- Inferência assíncrona.

## Versão 1.0 - Plataforma operacional

- RBAC completo.
- Organizações e times.
- Observabilidade com métricas e tracing.
- Backups automatizados.
- Deploy cloud-ready.
- Hardening de segurança.
- Documentação de operação.
- SDK/CLI sem duplicar regra de negócio.
