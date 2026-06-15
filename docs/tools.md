# Ferramentas e Dependencias Externas

Este documento separa dependencias Python, dependencias JavaScript e ferramentas de sistema/bioinformatica. Pacotes Python ficam nos arquivos `requirements*.txt`; ferramentas como `bcftools`, `samtools`, `SnpEff` e `Nextflow` precisam ser instaladas no sistema operacional ou na imagem Docker.

## Perfis de instalacao Python

Instalacao minima do backend:

```bash
pip install -r backend/requirements.txt
```

Desenvolvimento e testes:

```bash
pip install -r backend/requirements-dev.txt
```

Bioinformatica opcional:

```bash
pip install -r backend/requirements-bio.txt
```

Machine learning opcional:

```bash
pip install -r backend/requirements-ml.txt
```

Atalho a partir da raiz do monorepo:

```bash
pip install -r requirements.txt
```

## Dependencias JavaScript

O frontend usa Node.js 22.12+ e npm:

```bash
cd frontend
npm install
```

## Ferramentas obrigatorias para desenvolvimento local

- Python 3.11+
- Node.js 22.12+
- Docker
- Docker Compose
- PostgreSQL 16
- Redis 7

Com Docker Compose, PostgreSQL e Redis sao provisionados automaticamente.

A imagem Docker do backend instala `bcftools`, `samtools`, `primer3` e Java 17. `SnpEff` e `Nextflow` ficam documentados como ferramentas externas porque a v0.1 ainda nao executa anotacao real.

## Ferramentas de bioinformatica

Obrigatorias para a evolucao do modulo `variants` e para pipelines reais:

- `bcftools`: validacao, normalizacao e manipulacao de VCF/BCF.
- `samtools`: manipulacao de BAM/CRAM/FASTA indexado.
- `primer3`: desenho de primers.
- Java 17 ou superior: requisito para SnpEff e Nextflow.
- `SnpEff`: anotacao funcional de variantes.
- `Nextflow`: orquestracao futura de pipelines reprodutiveis.

Pacotes Python opcionais de bioinformatica:

- `biopython`
- `pysam`
- `cyvcf2`

## Instalacao no Windows

Recomendado para desenvolvimento:

1. Instale Docker Desktop.
2. Instale Python 3.11 ou superior.
3. Instale Node.js 22.12 LTS ou superior.
4. Instale Java 17 ou superior.
5. Use WSL2 para ferramentas nativas de bioinformatica quando possivel.

No WSL2 Ubuntu:

```bash
sudo apt update
sudo apt install -y bcftools samtools primer3 openjdk-17-jre-headless curl unzip
```

Nextflow:

```bash
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

SnpEff:

```bash
mkdir -p ~/tools
cd ~/tools
curl -L -o snpEff_latest_core.zip https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip
unzip snpEff_latest_core.zip
```

Exemplo de variavel de ambiente no PowerShell apontando para o JAR em instalacao local:

```powershell
$env:SNPEFF_JAR="C:\tools\snpEff\snpEff.jar"
```

## Instalacao no Linux

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv nodejs npm postgresql redis-server \
  bcftools samtools primer3 openjdk-17-jre-headless curl unzip
```

Nextflow:

```bash
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

SnpEff:

```bash
mkdir -p ~/tools
cd ~/tools
curl -L -o snpEff_latest_core.zip https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip
unzip snpEff_latest_core.zip
```

## Instalacao no macOS

Com Homebrew:

```bash
brew install python@3.11 node postgresql@16 redis bcftools samtools primer3 openjdk@17 nextflow
```

SnpEff:

```bash
mkdir -p ~/tools
cd ~/tools
curl -L -o snpEff_latest_core.zip https://snpeff.blob.core.windows.net/versions/snpEff_latest_core.zip
unzip snpEff_latest_core.zip
```

## Verificacao das ferramentas

```bash
python --version
node --version
npm --version
docker --version
docker compose version
psql --version
redis-server --version
bcftools --version
samtools --version
primer3_core --version
java -version
nextflow -version
```

Para SnpEff:

```bash
java -jar /caminho/para/snpEff/snpEff.jar -version
```

## Observacoes de escopo

Na v0.1, o parser VCF inicial nao exige `cyvcf2`, `SnpEff` ou `Nextflow` para funcionar. Essas ferramentas estao documentadas porque a arquitetura ja reserva portas para anotacao e pipelines, e elas serao necessarias nas proximas versoes.
