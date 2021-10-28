release: python manage.py migrate
web: gunicorn backend.wsgi --log-file -
worker: celery -A server worker --loglevel=info --concurrency=4 --max-tasks-per-child=1 --without-heartbeat --without-gossip --without-mingle