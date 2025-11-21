release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python create_admin.py >/dev/null 2>&1 || true
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
