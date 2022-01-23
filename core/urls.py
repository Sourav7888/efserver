from django.urls import path
from . import views

urlpatterns = [
    path("test_core_view/", views.CoreTestView.as_view(), name="test_core_view"),
    path("user/", views.UserPermission.as_view(), name="get_user_permission"),
    path("divisions/", views.DivisionList.as_view(), name="get_division_list"),
    path("facilities/", views.FacilityList.as_view(), name="get_facility_list"),
    path(
        "bulk-create-facility/",
        views.BulkCreateFacility.as_view(),
        name="bulk_create_facility",
    ),
]
