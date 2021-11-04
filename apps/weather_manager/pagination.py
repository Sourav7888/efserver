
  
from rest_framework.pagination import CursorPagination


class WeatherStationPg(CursorPagination):
    ordering = "climate_id"


class WeatherDataPg(CursorPagination):
    ordering = "date"