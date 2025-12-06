web: gunicorn myproject.wsgi:application -c gunicorn_config.py
release: python manage.py migrate && python manage.py collectstatic --noinput