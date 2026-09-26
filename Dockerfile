FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir ".[postgres]"

RUN useradd --create-home --uid 10001 productionos \
    && mkdir -p /data \
    && chown -R productionos:productionos /data
USER productionos
WORKDIR /data

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; response=urllib.request.urlopen('http://127.0.0.1:8787/health', timeout=3); raise SystemExit(0 if response.status == 200 else 1)"

ENTRYPOINT ["production-os"]
CMD ["control-plane","--database","/data/production.db","--auth-config","/data/auth.json","--host","0.0.0.0","--port","8787"]
