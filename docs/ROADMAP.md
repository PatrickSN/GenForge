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

* [ ] Configurar FastAPI.
* [ ] Configurar variáveis de ambiente.
* [ ] Configurar conexão com PostgreSQL.
* [ ] Configurar SQLAlchemy 2.x.
* [ ] Configurar Alembic.
* [ ] Criar endpoint `GET /health`.
* [ ] Configurar CORS.
* [ ] Criar tratamento básico de erros.
* [ ] Criar logs básicos da aplicação.

## Autenticação e usuários

* [ ] Criar modelo `User`.
* [ ] Implementar cadastro.
* [ ] Implementar login.
* [ ] Implementar autenticação JWT.
* [ ] Criar endpoint para consultar usuário autenticado.
* [ ] Armazenar senhas com hash seguro.
* [ ] Proteger endpoints privados.

## Projetos

* [ ] Criar modelo `Project`.
* [ ] Criar projeto.
* [ ] Listar projetos do usuário.
* [ ] Consultar detalhes de um projeto.
* [ ] Editar projeto.
* [ ] Excluir projeto.
* [ ] Garantir que usuários acessem apenas projetos autorizados.

## Arquivos e armazenamento

* [ ] Criar abstração de armazenamento.
* [ ] Criar armazenamento local inicial.
* [ ] Criar diretório por projeto.
* [ ] Registrar metadados dos arquivos.
* [ ] Aceitar upload de `.vcf` e `.vcf.gz`.
* [ ] Validar extensão.
* [ ] Validar existência do projeto.
* [ ] Registrar o usuário responsável pelo upload.
* [ ] Preparar migração futura para MinIO ou armazenamento compatível com S3.

## Variantes

* [ ] Criar modelo para arquivo VCF.
* [ ] Criar modelo para jobs de processamento.
* [ ] Criar modelo inicial de variante.
* [ ] Ler cabeçalho do VCF.
* [ ] Importar variantes básicas.
* [ ] Armazenar cromossomo, posição, referência e alelo alternativo.
* [ ] Criar paginação.
* [ ] Criar filtros por cromossomo, posição e qualidade.
* [ ] Exibir status de processamento.
* [ ] Registrar falhas de ingestão.

## Frontend

* [ ] Criar estrutura React + TypeScript + Vite.
* [ ] Criar tela de login.
* [ ] Criar tela de cadastro.
* [ ] Criar rotas protegidas.
* [ ] Criar dashboard inicial.
* [ ] Criar listagem de projetos.
* [ ] Criar formulário de novo projeto.
* [ ] Criar tela de detalhes do projeto.
* [ ] Criar upload de VCF.
* [ ] Criar tabela paginada de variantes.
* [ ] Exibir mensagens de erro amigáveis.

## Testes

* [ ] Testar endpoint de saúde.
* [ ] Testar cadastro.
* [ ] Testar login.
* [ ] Testar autorização.
* [ ] Testar CRUD de projetos.
* [ ] Testar upload de VCF pequeno.
* [ ] Testar ingestão inicial.
* [ ] Testar filtros de variantes.

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
