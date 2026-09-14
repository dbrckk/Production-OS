FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 productionos
USER productionos
WORKDIR /data

EXPOSE 8787

ENTRYPOINT ["production-os"]
CMD ["control-plane","--database","/data/production.db","--auth-config","/data/auth.json","--host","0.0.0.0","--port","8787"]
