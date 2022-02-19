from django.urls import path, include
from . import views


urlpatterns = [
    path(
        "station/", views.WeatherStationList.as_view(), name="get_weather_station_list"
    ),
    path("daily/", views.WeatherDataDaily.as_view(), name="get_weather_data_daily"),
    path(
        "monthly/",
        views.WeatherDataMonthly.as_view(),
        name="get_weather_data_monthly",
    ),
    path(
        "coordinate-data/", views.GetWeatherDataByCoord.as_view(), name="get_weather_data_by_coordinate"
    ),
]
