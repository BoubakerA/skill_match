FROM ubuntu:22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install project dependencies
COPY pyproject.toml .
COPY skill_match/ skill_match/
COPY app/ ./app
RUN uv sync

