from django.urls import path, include
from . import views
from . import dashboard_views

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
    path(
        "dashboard/",
        include(
            [
                path(
                    "energy-reduction/",
                    dashboard_views.CalculateTotalEnergyReduction.as_view(),
                    name="calculate_total_energy_reduction",
                ),
                path(
                    "energy-division-avg-ghg-pf/",
                    dashboard_views.CalculateDivisionGhgAvgPf.as_view(),
                    name="energy_division_ghg_pf",
                ),
            ]
        ),
    ),
]

urlpatterns = [path("", include(patterns))]
