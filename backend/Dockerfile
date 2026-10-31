FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt
COPY . .
RUN useradd --create-home app && chown -R app /app
USER app
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
