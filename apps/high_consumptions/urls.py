from django.urls import path, include
from . import views

patterns = [
    path(
        "generate-hc-report-by-facility/",
        views.GenerateHCReport.as_view(),
        name="generate-hc-report-by-facility",
    ),
    path("generate-hc", views.GenerateHC.as_view(), name="generate-hc"),
]

urlpatterns = [path("", include(patterns))]
