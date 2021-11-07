release: python manage.py migrate
web: gunicorn server.wsgi --log-file -
worker: celery -A server worker --beat --scheduler django --loglevel=info --concurrency=4 --max-tasks-per-child=1 --without-gossip --without-mingle -l INFO