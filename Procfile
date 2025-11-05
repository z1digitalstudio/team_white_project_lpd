release: python manage.py collectstatic --noinput
web: echo "Running migrations..." && python manage.py migrate --noinput && echo "Starting gunicorn..." && gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT --workers 3
