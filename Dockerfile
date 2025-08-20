FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and required files for hatchling
COPY pyproject.toml uv.lock LICENSE README.md ./

# Install dependencies
RUN uv sync --frozen --no-cache

RUN mkdir /app
COPY src/ app/

ARG VERSION
ENV VERSION=${VERSION}
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY gunicorn_settings.py /gunicorn_settings.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "-c", "/gunicorn_settings.py", "wsgi:application"]
