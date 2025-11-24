FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TMPDIR=/tmp

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /tmp /var/tmp /usr/tmp && \
    chmod 777 /tmp /var/tmp /usr/tmp && \
    chown -R root:root /tmp /var/tmp /usr/tmp

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python create_admin.py >/dev/null 2>&1 || true && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
