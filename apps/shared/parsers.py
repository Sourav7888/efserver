import pandas as pd
from datetime import datetime as dt
from typing import Union
from datetime import timedelta, datetime as dt
import csv


class QuerysetParser:

    """
    Parse a django queryset to pandas dataframes
    """

    def __init__(
        self,
        queryset=None,
    ):

        self.queryset = queryset

    def list_queryset(self, *args) -> list:
        """
        Evaluates the queryset and returns a list
        """
        if self.queryset.exists():
            return list(self.queryset.values())

        return []

    @staticmethod
    def listed_query_to_df(query: list[Union[str, float, int]]) -> pd.DataFrame:
        """
        Returns a dataframe from a listed query or list of dict.
        period must be of postgres format - yyyy-mm-dd
        """
        df = pd.DataFrame([])
        if query:
            df = pd.DataFrame(query)

        return df

    @staticmethod
    def transform_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Object specific transformation to apply to the dataframe
        """
        return df

    def evaluate_queryset_to_df(self, *args) -> pd.DataFrame:
        """
        Returns a dataframe of the given queryset
        """
        df = pd.DataFrame([])
        query = self.list_queryset(*args)

        if query:
            df = self.listed_query_to_df(query)
            if not df.empty:
                df = self.transform_df(df)

        return df


def parse_month_year(
    year: int, month: int, diff: int or None = None
) -> dt or (dt, dt) or None:
    """
    Parse month and year to provide a datetime object but also
    using diff provide the corresponding datetime object of a timedelta
    in months -> (date, diff_date)
    On errors it will return None
    """

    try:
        date = dt(year, month, 1)
        if diff:
            while diff != 1:
                if month > 1:
                    month -= 1
                elif month == 1:
                    year -= 1
                    month = 12
                diff -= 1
            return dt(year, month, 1), date
        return date
    except ValueError:
        return None


def parse_in_memory_csv(file) -> list[list[Union[str, int, float]]] or None:
    """
    Parse in memory file to a list of list or return none if an error occurs
    """
    try:
        if file.name[-3:] == "csv":

            reader = csv.reader(file.read().decode("utf-8").splitlines())
            data = [x for x in reader]
            return data

    except Exception as error:
        print(error)

    return None
