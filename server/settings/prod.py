from .base import *
import os
from dotenv import load_dotenv

load_dotenv()


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://dfae9344a94948199f8f594ded512b03@o946258.ingest.sentry.io/6041748",
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)


SECRET_KEY = os.environ.get("PRODUCTION_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ["efworkstation-server.herokuapp.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PRODUCTION_DATABASE_NAME"),
        "USER": os.environ.get("PRODUCTION_DATABASE_USER"),
        "PASSWORD": os.environ.get("PRODUCTION_DATABASE_PASSWORD"),
        "HOST": os.environ.get("PRODUCTION_DATABASE_HOST"),
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
        },
    },
    "weatherdatadb": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("WEATHER_DATABASE_NAME"),
        "USER": os.environ.get("WEATHER_DATABASE_USER"),
        "PASSWORD": os.environ.get("WEATHER_DATABASE_PASSWORD"),
        "HOST": os.environ.get("WEATHER_DATABASE_HOST"),
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
        },
    },
}

STATIC_URL = "/static/"

# << S3 STATIC BUCKETS CONFIG >>
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

AWS_ACCESS_KEY_ID = os.environ.get("PRODUCTION_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("PRODUCTION_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("PRODUCTION_AWS_STORAGE_BUCKET_NAME")

CELERY_BROKER_URL = os.environ.get("CLOUDAMQP_URL")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_IGNORE_RESULT = True

# Auth0 config
AUTH0_AUDIENCE = os.environ.get("PRODUCTION_AUTH0_AUDIENCE")
AUTH0_DOMAIN = os.environ.get("PRODUCTION_AUTH0_DOMAIN")

JWT_AUTH["JWT_AUDIENCE"] = AUTH0_AUDIENCE
JWT_AUTH["JWT_ISSUER"] = AUTH0_DOMAIN

EMAIL_HOST = os.environ.get("PRODUCTION_MAILGUN_SMTP_SERVER")
EMAIL_PORT = os.environ.get("PRODUCTION_MAILGUN_SMTP_PORT")
EMAIL_HOST_USER = os.environ.get("PRODUCTION_MAILGUN_SMTP_USER")
EMAIL_HOST_PASSWORD = os.environ.get("PRODUCTION_MAILGUN_SMTP_PASSWORD")

CORS_ALLOWED_ORIGINS = [
    "https://efworkstation-client.herokuapp.com",
    "https://efworkstation-server.herokuapp.com",
    "https://ems.enerfrog-workstation.app",
]
