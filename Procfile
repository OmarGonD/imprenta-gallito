release: python manage.py migrate
web: python manage.py collectstatic --noinput; bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT settings.py 
web: gunicorn stickers_gallito.wsgi --log-file -