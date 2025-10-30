release: python manage.py collectstatic --noinput
web: gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT --workers 3
