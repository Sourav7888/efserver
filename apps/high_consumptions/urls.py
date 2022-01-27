from django.urls import path, include
from . import views

patterns = [
    path(
        "generate-hc-report/",
        views.GenerateHCReport.as_view(),
        name="generate-hc-report",
    )
]

urlpatterns = [path("", include(patterns))]
