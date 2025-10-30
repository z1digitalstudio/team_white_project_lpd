# Usar Python 3.11 como imagen base
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TMPDIR=/tmp

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Crear directorio temporal y dar permisos
RUN mkdir -p /tmp /var/tmp /usr/tmp && \
    chmod 777 /tmp /var/tmp /usr/tmp && \
    chown -R root:root /tmp /var/tmp /usr/tmp

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn mysite.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]