web: gunicorn backend.wsgi --log-file -
worker: celery -A backend worker --loglevel=info --concurrency=4 --max-tasks-per-child=1 --without-heartbeat --without-gossip --without-mingle