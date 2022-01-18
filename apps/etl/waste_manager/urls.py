from django.urls import path, include
from . import views


patterns = [
    path("", views.GetWasteData.as_view(), name="get_waste_data"),
    path("yearly/", views.GetWasteDataYearly.as_view(), name="get_waste_data_yearly"),
    path("total/", views.GetWasteTotalFromStart.as_view(), name="get_waste_data_total"),
    path(
        "recycling-rate/",
        views.GetRecyclingRate.as_view(),
        name="get_waste_recycling_rate",
    ),
    path(
        "contribution-by-name/",
        views.GetWasteContributionByName.as_view(),
        name="get_waste_contribution_by_name",
    ),
    path(
        "bulk-create-waste-data/",
        views.BulkCreateWasteData.as_view(),
        name="waste_manager_test",
    ),
]

urlpatterns = [path("", include(patterns))]
