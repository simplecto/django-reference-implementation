release: python manage.py migrate
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
