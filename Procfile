release: echo "Starting release phase..." && python manage.py migrate --noinput && echo "Migrations completed successfully" && python manage.py collectstatic --noinput && echo "Static files collected"
web: gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT --workers 3
