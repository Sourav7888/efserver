from django.urls import path, include
from . import views


patterns = [
    path(
        "",
        views.GetInvestigations.as_view(),
        name="get_investigations",
    ),
    path(
        "create/",
        views.CreateInvestigation.as_view(),
        name="create_investigation",
    ),
    path(
        "create-investigation-by-hc/",
        views.CreateInvestigationByHC.as_view(),
        name="create_investigation_by_hc",
    ),
    path(
        "update/<str:investigation_id>",
        views.UpdateInvestigation.as_view(),
        name="update_investigation",
    ),
]

urlpatterns = [path("", include(patterns))]
