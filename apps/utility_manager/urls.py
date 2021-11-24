from django.urls import path, include
from . import views

patterns = [
    path(
        "bulk-create-utility/",
        views.BulkCreateUtility.as_view(),
        name="bulk_create_utility",
    ),
    path(
        "division-utility/",
        views.GetDivisionUtility.as_view(),
        name="get_division_utility",
    ),
    path(
        "facility-utility/",
        views.GetFacilityUtility.as_view(),
        name="get_facility_utility",
    ),
]

urlpatterns = [path("", include(patterns))]
