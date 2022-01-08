from django.urls import path, include
from . import views


patterns = [path("", views.GetWasteData.as_view(), name="waste_manager_test")]

urlpatterns = [path("", include(patterns))]
