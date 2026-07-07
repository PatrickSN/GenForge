# GenForge — Roadmap de Desenvolvimento

## 1. Visão Geral

GenForge é uma plataforma web integrada de bioinformática voltada inicialmente para genética vegetal, análise de variantes e mutagênese EMS.

A evolução do sistema deve ocorrer de forma incremental. Cada fase precisa gerar uma versão utilizável, testável e documentada antes do início da fase seguinte.

A arquitetura deve permitir expansão futura para GWAS, seleção genômica, inteligência artificial, design de primers e pipelines NGS sem exigir a reescrita dos módulos existentes.

---

## 2. Princípios de Desenvolvimento

* Implementar uma fase por vez.
* Priorizar um MVP funcional antes de adicionar recursos avançados.
* Manter regras de negócio fora dos routers.
* Criar migrations para alterações no banco.
* Adicionar testes para funcionalidades novas.
* Não armazenar arquivos genômicos grandes diretamente no PostgreSQL.
* Registrar metadados no banco e armazenar arquivos em disco ou object storage.
* Documentar comandos, decisões arquiteturais e limitações conhecidas.
* Manter módulos futuros isolados até que entrem oficialmente no escopo.

---

## 3. Legenda de Status

* `[ ]` Não iniciado
* `[~]` Em desenvolvimento
* `[x]` Concluído
* `[!]` Bloqueado ou pendente de correção

Atualize os itens conforme o avanço real do projeto.

---

# Fase 1 — Fundação da Plataforma e MVP de Variantes

## Objetivo

Criar uma primeira versão utilizável da plataforma com autenticação, projetos, upload de arquivos VCF, ingestão inicial e consulta de variantes.

## Backend

* [x] Configurar FastAPI.
* [x] Configurar variáveis de ambiente.
* [x] Configurar conexão com PostgreSQL.
* [x] Configurar SQLAlchemy 2.x.
* [x] Configurar Alembic.
* [x] Criar endpoint `GET /health`.
* [x] Configurar CORS.
* [x] Criar tratamento básico de erros.
* [x] Criar logs básicos da aplicação para requisições HTTP e jobs de variantes.

## Autenticação e usuários

* [x] Criar modelo `User`.
* [x] Implementar cadastro.
* [x] Implementar login.
* [x] Implementar autenticação JWT.
* [x] Criar endpoint para consultar usuário autenticado.
* [x] Armazenar senhas com hash seguro.
* [x] Proteger endpoints privados.

## Projetos

* [x] Criar modelo `Project`.
* [x] Criar projeto.
* [x] Listar projetos do usuário.
* [x] Consultar detalhes de um projeto.
* [x] Editar projeto.
* [x] Excluir projeto.
* [x] Garantir que usuários acessem apenas projetos autorizados.

## Arquivos e armazenamento

* [x] Criar abstração de armazenamento.
* [x] Criar armazenamento local inicial.
* [x] Criar diretório por projeto.
* [x] Registrar metadados dos arquivos.
* [x] Aceitar upload de `.vcf` e `.vcf.gz`.
* [x] Validar extensão.
* [x] Validar existência do projeto.
* [x] Registrar o usuário responsável pelo upload.
* [~] Preparar migração futura para MinIO ou armazenamento compatível com S3.

## Variantes

* [x] Criar modelo para arquivo VCF.
* [x] Criar modelo para jobs de processamento.
* [x] Criar modelo inicial de variante.
* [x] Ler cabeçalho do VCF.
* [x] Importar variantes básicas.
* [x] Armazenar cromossomo, posição, referência e alelo alternativo.
* [x] Criar paginação.
* [~] Criar filtros por cromossomo, posição, gene e impacto; filtro de qualidade ainda pendente.
* [x] Exibir status de processamento.
* [x] Registrar falhas de ingestão.

## Frontend

* [x] Criar estrutura React + TypeScript + Vite.
* [x] Criar tela de login.
* [x] Criar tela de cadastro.
* [x] Criar rotas protegidas.
* [x] Criar dashboard inicial.
* [x] Criar listagem de projetos.
* [x] Criar formulário de novo projeto.
* [x] Criar tela de detalhes do projeto.
* [x] Editar e excluir projetos.
* [x] Criar upload de VCF.
* [x] Criar tabela paginada de variantes.
* [x] Exibir histórico de arquivos VCF e jobs de processamento.
* [x] Exibir mensagens de erro amigáveis.

## Testes

* [x] Testar endpoint de saúde.
* [x] Testar cadastro.
* [x] Testar login.
* [x] Testar autorização.
* [x] Centralizar fixtures pytest para usuario, autenticacao, projeto e VCF minimo.
* [x] Testar endpoint de usuario autenticado e listagem de usuarios protegida.
* [x] Testar CRUD de projetos.
* [x] Testar upload de VCF pequeno.
* [~] Testar ingestão inicial com parser e job; falta smoke com worker/Celery real no servidor.
* [x] Testar filtros de variantes implementados na API por cromossomo, gene, impacto e intervalo de posicao.

## Critérios para concluir a Fase 1

A fase estará concluída quando:

1. O backend iniciar sem erros.
2. As migrations forem aplicadas corretamente.
3. Um usuário conseguir cadastrar-se e autenticar-se.
4. Um usuário conseguir criar um projeto.
5. Um arquivo VCF pequeno puder ser enviado.
6. O sistema registrar o processamento.
7. As variantes forem persistidas no banco.
8. A interface listar variantes com paginação e filtros.
9. Os testes essenciais passarem.
10. O README explicar como executar o MVP.

## Status em 2026-07-07

A Fase 1 esta funcional para testes manuais com autenticacao, projetos, upload
VCF, consulta paginada de variantes e visualizacao de arquivos/jobs. A camada
inicial de pytest cobre endpoints de auth/users, projects, upload/listagem de
arquivos/jobs e listagem filtrada de variantes. As migrations geram SQL offline
com sucesso, mas a aplicacao online em PostgreSQL de desenvolvimento ainda
precisa ser revalidada quando houver banco local ou Docker disponivel. Antes de
declarar a fase concluida, ainda faltam validar worker Celery/Redis real no
servidor Linux e manter a validacao Alembic online no fluxo regular.

## Status adicional em 2026-07-07

A saida do servidor registrou Alembic online em `202606260001 (head)` e build
frontend concluido. O backup com `pg_dump "$DATABASE_URL"` falhou porque o shell
nao tinha `DATABASE_URL` exportado, a porta 8000 ja estava ocupada durante duas
tentativas de Uvicorn, e o worker Celery ainda nao respondeu ao `inspect ping`.
Foram adicionados logs basicos da API/worker e um smoke script para validar
auth, users, projects, upload VCF, arquivos/jobs e variantes com mensagens de
falha acionaveis. Tambem foi corrigido o delete de projetos com VCF/job
associado para respeitar os cascades do banco.

---

# Fase 2 — Anotação e Priorização de Variantes

## Objetivo

Transformar a ingestão inicial em um fluxo de análise útil para pesquisadores.

## Escopo

* [ ] Integrar `bcftools`.
* [ ] Integrar `SnpEff`.
* [ ] Criar configuração por organismo e referência.
* [ ] Armazenar gene, efeito e impacto.
* [ ] Filtrar por `HIGH`, `MODERATE`, `LOW` e `MODIFIER`.
* [ ] Filtrar por profundidade, qualidade e frequência alélica.
* [ ] Criar ranking inicial de variantes.
* [ ] Exportar resultados em CSV e VCF filtrado.
* [ ] Criar relatório resumido.
* [ ] Adicionar logs detalhados de execução.
* [ ] Preparar processamento assíncrono.

## Entregável

Módulo funcional de priorização de variantes.

---

# Fase 3 — Banco de Mutantes EMS

## Objetivo

Criar um catálogo pesquisável de mutações induzidas por EMS.

## Escopo

* [ ] Identificar assinaturas típicas de EMS.
* [ ] Associar variantes a genes.
* [ ] Associar variantes a fenótipos.
* [ ] Criar cadastro de experimentos.
* [ ] Criar cadastro de amostras.
* [ ] Criar busca por gene.
* [ ] Criar busca por cromossomo e posição.
* [ ] Criar busca por efeito.
* [ ] Criar histórico de linhagens.
* [ ] Preparar integração com navegador genômico.

## Entregável

Catálogo web de mutantes EMS.

---

# Fase 4 — Design de Primers

## Objetivo

Gerar primers a partir de sequências ou variantes selecionadas.

## Escopo

* [ ] Integrar `Primer3`.
* [ ] Aceitar sequência FASTA.
* [ ] Gerar primer forward e reverse.
* [ ] Calcular Tm.
* [ ] Calcular conteúdo GC.
* [ ] Validar tamanho esperado do amplicon.
* [ ] Permitir geração a partir de uma variante.
* [ ] Exportar tabela de primers.
* [ ] Avaliar especificidade em fase posterior.

## Entregável

Ferramenta básica de desenho de primers.

---

# Fase 5 — GWAS

## Objetivo

Executar análises de associação genômica ampla a partir de genótipos e fenótipos.

## Escopo

* [ ] Definir formato de entrada fenotípica.
* [ ] Validar correspondência entre amostras.
* [ ] Integrar ferramentas de QC.
* [ ] Integrar PLINK.
* [ ] Calcular PCA.
* [ ] Calcular matriz de kinship.
* [ ] Integrar GAPIT ou GEMMA.
* [ ] Gerar Manhattan Plot.
* [ ] Gerar QQ Plot.
* [ ] Listar SNPs significativos.
* [ ] Relacionar SNPs a genes candidatos.
* [ ] Exportar relatório.

## Entregável

Módulo web de GWAS reproduzível.

---

# Fase 6 — Seleção Genômica

## Objetivo

Predizer desempenho genético com modelos estatísticos e Machine Learning.

## Escopo

* [ ] Criar matriz de genótipos.
* [ ] Importar fenótipos.
* [ ] Criar divisão treino/teste.
* [ ] Implementar validação cruzada.
* [ ] Implementar RR-BLUP.
* [ ] Implementar GBLUP.
* [ ] Integrar Random Forest.
* [ ] Integrar XGBoost.
* [ ] Comparar métricas.
* [ ] Criar ranking de indivíduos.
* [ ] Exportar predições.

## Entregável

Dashboard de seleção genômica.

---

# Fase 7 — Inteligência Artificial Aplicada à Genômica

## Objetivo

Adicionar modelos avançados sem substituir prematuramente métodos estatísticos tradicionais.

## Escopo

* [ ] Definir casos de uso prioritários.
* [ ] Criar versionamento de datasets.
* [ ] Criar versionamento de modelos.
* [ ] Registrar hiperparâmetros.
* [ ] Registrar métricas.
* [ ] Avaliar embeddings de proteínas.
* [ ] Avaliar ESM e ProtBERT.
* [ ] Criar predição experimental de função gênica.
* [ ] Criar comparação com baselines.
* [ ] Documentar limitações e incertezas.

## Entregável

Módulo experimental de IA com rastreabilidade.

---

# Fase 8 — Pipelines NGS

## Objetivo

Automatizar o processamento desde dados brutos até arquivos VCF ou matrizes de expressão.

## Escopo

* [ ] Integrar Nextflow.
* [ ] Criar pipeline mínimo FASTQ → QC → alinhamento → BAM → VCF.
* [ ] Integrar FastQC.
* [ ] Integrar samtools.
* [ ] Integrar BWA para DNA.
* [ ] Avaliar STAR ou HISAT2 para RNA-Seq.
* [ ] Registrar versões das ferramentas.
* [ ] Registrar parâmetros.
* [ ] Gerar logs.
* [ ] Gerar relatórios.
* [ ] Preparar execução em HPC.

## Entregável

Pipeline NGS reproduzível.

---

# 4. Melhorias Transversais

Essas melhorias devem ser implementadas gradualmente:

* [ ] Processamento assíncrono com Redis e Celery.
* [ ] Object storage com MinIO ou solução compatível com S3.
* [ ] Controle de acesso por projeto.
* [ ] Compartilhamento entre usuários.
* [ ] Auditoria de ações.
* [ ] Monitoramento.
* [ ] Backups.
* [ ] CI/CD.
* [ ] Documentação da API.
* [ ] Versionamento de referências genômicas.
* [ ] Registro de versões das ferramentas bioinformáticas.
* [ ] Exportação de relatórios PDF.

---

# 5. Priorização Atual

A prioridade imediata é concluir a Fase 1.

Não iniciar GWAS, EMS, IA, seleção genômica, primers ou pipelines NGS antes de o MVP de variantes estar funcional e testado.

---

# 6. Controle de Versões

Utilizar branches por tarefa ou fase:

```bash
git checkout -b fase-1-core
git checkout -b fase-2-annotation
```

Utilizar commits pequenos e claros:

```bash
git commit -m "feat(auth): implementa login JWT"
git commit -m "feat(projects): adiciona CRUD de projetos"
git commit -m "feat(variants): adiciona upload de VCF"
git commit -m "test(auth): adiciona testes de autenticação"
git commit -m "docs(roadmap): atualiza progresso da fase 1"
```
