# scrapAI backend — produção
#
# Base: imagem oficial Playwright Python (Ubuntu 24.04 Noble) com Chromium e
# dependências de sistema embutidas (documentação oficial:
# https://playwright.dev/python/docs/docker). A versão do Playwright foi
# pinada para casar com a versão instalada em requirements (playwright 1.62.0).
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# 1. Dependências Python primeiro (cache de camada)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Garantir browser Chromium presente para o Playwright/Crawl4AI instalados
#    (idempotente: se o browser da imagem já for compatível, nada é baixado)
RUN playwright install chromium

# 3. Código da aplicação
COPY app ./app

EXPOSE 8000

# Produção: sem --reload. Porta configurável via PORT (padrão 8000).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
