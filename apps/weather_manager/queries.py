from .models import WeatherStation, WeatherData
import pandas as pd
from datetime import datetime as dt
from math import radians
from .processors import calculate_closest_station
from .parsers import WeatherDataPr
from django.db.models import Q
from typing import Union

# @TODO: Integration Test
def query_weather_stations_as_dataframe(format=None) -> pd.DataFrame:
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


# @TODO: Integration Test
def query_weather_data_as_dataframe(
    climate_id: str,
    timeframe: Union[str, None] = None,
    format_date: bool = False,  # If format date return an additional col with format %Y-%m-%d
    # Only work if timeframe is set
    **kwargs
) -> pd.DataFrame:
    """
    Query weather data using the climate id
    Can pass as kwargs date__gte etc... for additional filters
    """

    query = WeatherData.objects.filter(climate_id=climate_id, **kwargs).select_related(
        "climate_id"
    )

    if timeframe == "Monthly":
        data = WeatherDataPr(queryset=query).get_monthly_data()

        if format_date:
            data["date"] = (
                data["year"].astype(str) + "-" + data["month"].astype(str) + "-01"
            )
            data["date"] = data["date"].apply(lambda x: dt.strptime(x, "%Y-%m-%d"))

        return data

    df = pd.DataFrame([])
    if query.exists():
        df = pd.DataFrame(list(query.values()))

    return df


# @TODO: Integration Test
def query_closest_weather_station(lat: float, lng: float) -> dict[str, str]:
    """
    Gets the closest weather station based on the lat and lng
    """
    stations = query_weather_stations_as_dataframe(format="Processed")
    closest = calculate_closest_station(stations, lat, lng)

    return closest


# @TODO: Integration Test
def query_coord_weather_data(lat: float, lng: float, **kwargs) -> pd.DataFrame:
    """
    Query weather data using the lat and lng
    additional kwargs related to weather model
    """
    # get the closest station to the coordinate
    station = query_closest_weather_station(lat, lng)["climate_id"]

    # get the weather data for the closest station
    weather = query_weather_data_as_dataframe(
        station, timeframe="Monthly", format_date=True, **kwargs
    )

    return weather


# @TODO: Integration Test
def query_coord_specific_month_weather_data(
    lat: float,
    lng: float,
    month: int,
    min_year: int = None,  # required min_year
    max_year: int = None,  # required max_year
) -> pd.DataFrame:
    """
    Query the monthly weather stats for a climate id includes all
    data of the same month between the min and max year
    """
    if not min_year or not max_year:
        raise ValueError("min_year and max_year are required")

    # get the closest station to the coordinate
    station = query_closest_weather_station(lat, lng)["climate_id"]

    weather = query_weather_data_as_dataframe(
        station,
        timeframe="Monthly",
        format_date=True,
        date__month=month,
        date__year__gte=min_year,
        date__year__lte=max_year,
    )
    return weather
