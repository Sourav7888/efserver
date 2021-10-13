from .base import *
import os
from dotenv import load_dotenv

load_dotenv()

# Auth0 config
AUTH0_AUDIENCE = os.getenv("PRODUCTION_AUTH0_AUDIENCE")
AUTH0_DOMAIN = os.getenv("PRODUCTION_AUTH0_DOMAIN")

JWT_AUTH["JWT_AUDIENCE"] = AUTH0_AUDIENCE
JWT_AUTH["JWT_ISSUER"] = AUTH0_DOMAIN
