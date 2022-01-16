from django.urls import path, include
from . import views


patterns = [path("renewables", views.GetRenewables.as_view(), name="get_renewables")]

urlpatterns = [path("", include(patterns))]
