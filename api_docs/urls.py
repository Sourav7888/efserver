from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path, path
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="EFServer API",
        default_version="v1",
        description="Powered by Enerfrog",
        terms_of_service="",
        contact=openapi.Contact(email="tantely.raza@enerfrog.com"),
        license=openapi.License(name="Private"),
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path(
        "get-staples-swagger-schema/",
        views.GetStaplesSwaggerSchema.as_view(),
        name="get-staples-swagger-schema",
    ),
]
