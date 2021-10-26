from django.urls import path, include
from . import views


patterns = [
    path(
        "create/",
        views.CreateInvestigation.as_view(),
        name="create_investigation",
    ),
    path(
        "update/<str:investigation_id>",
        views.UpdateInvestigation.as_view(),
        name="update_investigation",
    ),
]

urlpatterns = [path("investigations/", include(patterns))]
