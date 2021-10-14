from django.urls import path, include
from . import views

urlpatterns = [path("", views.CoreTestView.as_view(), name="test_core_view")]
