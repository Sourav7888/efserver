from django.urls import path, include
from . import views

patterns = [
    path(
        "generate-hc-report-by-facility/",
        views.GenerateHCReport.as_view(),
        name="generate-hc-report-by-facility",
    )
]

urlpatterns = [path("", include(patterns))]
