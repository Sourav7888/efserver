from django.urls import path, include
from . import views


patterns = []

urlpatterns = [path("", include(patterns))]