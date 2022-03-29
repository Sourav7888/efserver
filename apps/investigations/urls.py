from django.urls import path, include
from . import views


patterns = [
    path(
        "",
        views.GetInvestigations.as_view(),
        name="get_investigations",
    ),
    path(
        "get-assigned-investigations/",
        views.GetAssignedInvestigations.as_view(),
        name="get_assigned_investigations",
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
    path(
        "report/send-hc-investigation-report/",
        views.SendHCInvestigationReport.as_view(),
        name="send_hc_investigation_report",
    ),
]

urlpatterns = [path("", include(patterns))]
