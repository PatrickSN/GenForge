FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      gcc \
      git \
      openjdk-17-jre-headless \
      unzip \
      libbz2-dev \
      liblzma-dev \
      libpq-dev \
      zlib1g-dev \
      bcftools \
      samtools \
      primer3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
