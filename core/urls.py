from django.urls import path, include
from . import views

urlpatterns = [
    path("test_core_view/", views.CoreTestView.as_view(), name="test_core_view"),
    path("user/", views.UserPermission.as_view(), name="user_permission"),
]
