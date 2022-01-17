from django.urls import path, include
from . import views


patterns = [
    path(
        "renewables-yearly/",
        views.GetRenewablesYearly.as_view(),
        name="get_renewables_yearly",
    ),
    path("led-list/", views.GetLedList.as_view(), name="get_led_list"),
]

urlpatterns = [path("", include(patterns))]
