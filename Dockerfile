FROM docker.io/library/python:3.11-slim-bullseye as base

LABEL about.home="https://github.com/Clinical-Genomics/genotype-api"
LABEL about.tags="Genotype API"


ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400
ENV VERSION="v1"

ENV DB_URI="sqlite:///database.db"
ENV DB_NAME="database.db"
ENV HOST="localhost"

EXPOSE 8000

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install app requirements
RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

CMD gunicorn \
    --workers=$GUNICORN_WORKERS \
    --bind=$GUNICORN_BIND  \
    --threads=$GUNICORN_THREADS \
    --timeout=$GUNICORN_TIMEOUT \
    --proxy-protocol \
    --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
    --log-syslog \
    --access-logfile - \
    --log-level="debug" \
    --worker-class=uvicorn.workers.UvicornWorker \
    genotype_api.api.app:app
