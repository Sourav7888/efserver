"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import os
from dotenv import load_dotenv

load_dotenv()

# Declare your apis here
api_paths = [
    # Where all of the permissions and foreign keys are
    path("core/", include("core.urls")),
    # Investigations ie: High Consumptions etc...
    path("investigations/", include("apps.investigations.urls")),
    # Path to api documentation
    path("docs/", include("api_docs.urls")),
]

# Admin link for prod
prod_admin_link = "04a314d8-1d20-406a-af37-d43a97a0f5a9/"

# Only add these when we are in dev
if (
    os.getenv("ENV_TYPE") == "DEVELOPMENT"
    or os.environ.get("ENV_TYPE") == "DEVELOPMENT"
):
    import debug_toolbar

    prod_admin_link = "admin/"

    # Debug toolbar
    api_paths.append(path("__debug__", include(debug_toolbar.urls)))

    # Sentry error test
    def trigger_error(request):
        division_by_zero = 1 / 0

    api_paths.append(path("test-sentry", trigger_error))

# Url patterns
urlpatterns = [
    path(prod_admin_link, admin.site.urls),
    path(
        "api/",
        include(api_paths),
    ),
]
