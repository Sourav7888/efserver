from django.urls import path, include
from . import views

patterns = [path("", views.TestView.as_view(), name="test")]

urlpatterns = [path("", include(patterns))]
