from django.urls import path, include
from . import views


patterns = [
    path("renewables", views.GetRenewables.as_view(), name="get_renewables"),
    path("led-list", views.GetLedList.as_view(), name="get_led_list"),
]

urlpatterns = [path("", include(patterns))]
