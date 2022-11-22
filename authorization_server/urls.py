from django.urls import path, include
from . import views

patterns = [
    path(
        "user/<str:user_id>",
        views.GetUserInfo.as_view(),
        name="authorization_server_get_user_info",
    ),
    path("my-info", views.GetMyInfo.as_view(), name="authorization_server_get_my_info"),
]

urlpatterns = [
    path("", include(patterns)),
]
