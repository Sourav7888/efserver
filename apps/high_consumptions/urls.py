from django.urls import path, include
from . import views

patterns = [
    path(
        "generate-hc-report-by-facility/",
        views.GenerateHCReportByFacility.as_view(),
        name="generate-hc-report-by-facility",
    ),
    path("generate-hc/", views.GenerateHC.as_view(), name="generate-hc"),
    path("get-generated-hc/", views.GetGeneratedHC.as_view(), name="get-generated-hc"),
    path(
        "generate-hc-by-division/",
        views.GenerateHCByDivision.as_view(),
        name="generate-hc-by-division",
    ),
    path(
        "delete-generated-hc/",
        views.DeleteGeneratedHC.as_view(),
        name="delete_generated_hc",
    ),
    path(
        "get-hc-report-tracker/",
        views.GetHCReportTracker.as_view(),
        name="get-hc-report-tracker",
    ),
]

urlpatterns = [path("", include(patterns))]
