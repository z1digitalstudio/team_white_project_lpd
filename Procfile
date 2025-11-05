release: python manage.py collectstatic --noinput
web: python manage.py migrate --noinput && gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT --workers 3
