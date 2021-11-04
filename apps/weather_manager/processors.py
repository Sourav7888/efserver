from math import radians
from sklearn.metrics.pairwise import haversine_distances
from typing import Union
import pandas as pd


def calculate_closest_station(
    df, lat: Union[float, None] = None, long: Union[float, None] = None
):
    """
    Must pass a dataframe of a list of all weather stations with coordinates (in radians)
    Return the closest weather station (dict) or None |
    Uses the harvesine formula to calculate the closest point
    """

    if not df.empty or df:
        df["point_lat"] = radians(lat)
        df["point_long"] = radians(long)
        df["distance"] = df.apply(
            lambda row: haversine_distances(
                [
                    [row["point_lat"], row["point_long"]],
                    [row["latitude"], row["longitude"]],
                ]
            )[0][1]
            * 6371,  # Earth radius in km
            axis=1,
        )

        weather_station = df[df["distance"] == df["distance"].min(axis=0)]
        weather_station.reset_index(drop=True, inplace=True)

        return weather_station.to_dict("records")[0]

    return df
