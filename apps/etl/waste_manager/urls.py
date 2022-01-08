from django.urls import path, include
from . import views


patterns = [
    path("", views.GetWasteData.as_view(), name="waste_manager_test"),
    path(
        "bulk-create-waste-data/",
        views.BulkCreateWasteData.as_view(),
        name="waste_manager_test",
    ),
]

urlpatterns = [path("", include(patterns))]
