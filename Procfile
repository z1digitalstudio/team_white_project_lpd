release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py create_superuser_if_not_exists --noinput || true
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
