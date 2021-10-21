import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Set the default Django settings module for the 'celery' program.
if os.getenv("ENV_TYPE") == "DEVELOPMENT":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings.dev")
elif os.getenv("ENV_TYPE") == "PRODUCTION":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings.prod")

app = Celery(
    "server",
)

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()