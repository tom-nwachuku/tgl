# TGL connector Docker image.
# Build:  docker build -t tgl-connector .
# Run:    docker run -e PORT=8000 -p 8000:8000 tgl-connector
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/connector/

# Drop root privileges for the runtime user.
RUN useradd --create-home --no-log-init appuser \
    && chown -R appuser:appuser /app
USER appuser

# $PORT is set by the host platform; default 8000 for local runs.
# --factory because create_app() is an app factory, not an app instance.
CMD ["sh", "-c", "uvicorn --factory connector.server:create_app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]
