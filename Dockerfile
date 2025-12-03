FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --only main

COPY app ./app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]














