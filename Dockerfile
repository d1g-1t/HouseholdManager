FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.7.1

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry lock --no-update \
    && poetry export -f requirements.txt --without-hashes -o requirements.txt

FROM base AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p media staticfiles logs ml_models

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]