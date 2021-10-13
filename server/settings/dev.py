from server.settings.base import *
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("DEVELOPMENT_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DEVELOPMENT_DATABASE_NAME"),
        "USER": os.getenv("DEVELOPMENT_DATABASE_USER"),
        "PASSWORD": os.getenv("DEVELOPMENT_DATABASE_PASSWORD"),
        "HOST": os.getenv("DEVELOPMENT_DATABASE_HOST"),
        "PORT": "5432",
    },
}

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

STATIC_URL = "/static/"

AWS_ACCESS_KEY_ID = os.getenv("DEVELOPMENT_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("DEVELOPMENT_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("DEVELOPMENT_AWS_STORAGE_BUCKET_NAME")

# Auth0 config
AUTH0_AUDIENCE = os.getenv("DEVELOPMENT_AUTH0_AUDIENCE")
AUTH0_DOMAIN = os.getenv("DEVELOPMENT_AUTH0_DOMAIN")

JWT_AUTH["JWT_AUDIENCE"] = AUTH0_AUDIENCE
JWT_AUTH["JWT_ISSUER"]= AUTH0_DOMAIN