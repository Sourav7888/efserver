from .models import WeatherStation, WeatherData
import pandas as pd
from datetime import datetime as dt
from math import radians
from .processors import calculate_closest_station
from .parsers import WeatherDataPr
from django.db.models import Q


def query_weather_stations_as_df(format=None) -> pd.DataFrame:
    """
    Return a dataframe of the weather stations
    """
    query = list(WeatherStation.objects.all().values())
    weather_stations = pd.DataFrame.from_records(query)

    if not weather_stations.empty:
        if format == "Raw":  # Returns a 'raw' dataframe of the query
            return weather_stations

        elif format == "Processed":  # returns coordinates in radians
            weather_stations["latitude"] = weather_stations["latitude"].apply(
                lambda x: radians(x)
            )
            weather_stations["longitude"] = weather_stations["longitude"].apply(
                lambda x: radians(x)
            )
            return weather_stations

    return weather_stations


def query_weather_data_as_df(climate_id: str, **kwargs) -> pd.DataFrame:
    """
    Query weather data using the climate id
    Can pass as kwargs date__gte etc... for additional filters
    """

    query = WeatherData.objects.filter(climate_id=climate_id, **kwargs)

    df = pd.DataFrame([])
    if query.exists():
        df = pd.DataFrame(list(query.values()))

    return df


def query_closest_weather_stations(lat: float, lng: float) -> dict[str, str]:
    stations = query_weather_stations_as_df(format="Processed")
    closest = calculate_closest_station(stations, lat, lng)

    return closest


def query_performance_weather_data(
    climate_id: str, period: tuple[dt, dt]
) -> pd.DataFrame:
    """
    Query weather data including past month relative to a period
    """
    weather_parser = WeatherDataPr(
        queryset=WeatherData.objects.filter(
            Q(
                climate_id=climate_id,
                date__gte=period[0],
                date__lte=period[1],
            )
            | Q(
                climate_id=climate_id,
                date__month=period[1].month,
                date__year__lte=period[1].year,
            )
        ).select_related("climate_id")
    )
    weather = weather_parser.get_monthly_data()
    return weather
