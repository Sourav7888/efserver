import pandas as pd
from datetime import datetime as dt
from typing import Union
from .cs_exceptions import InvalidDateFormat


def group_and_sum(
    df,
    year: bool = False,
    month: bool = False,
    group_by: str or None = None,
    round_by: int = 2,
):
    """
    Groups and sum dataframe by a column datetime type
    """

    if group_by:
        if year and month:
            df = df.groupby(
                [
                    df[group_by].dt.year.rename("year"),
                    df[group_by].dt.month.rename("month"),
                ]
            ).sum()
        elif month:
            df = df.groupby([df[group_by].dt.month.rename("month")]).sum()
        elif year:
            df = df.groupby([df[group_by].dt.year.rename("year")]).sum()

    return df.round(round_by)


def convert_year_month_to_dt(
    df: pd.DataFrame, year="year", month="month"
) -> pd.DataFrame:
    """
    Convert a dataframe with separate year and month into one column of
    datetime object
    """
    df["date"] = df[year].astype(str) + "-" + df[month].astype(str) + "-" + "1"
    df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%Y-%m-%d"))
    df.drop(["year", "month"], inplace=True, axis=1)
    return df


def calculate_diff(og: int, nw: int, rounding: int = 2) -> Union[int, float]:
    """
    Calculates the diff between two numbers in percentage to a min of -100 and max of 100
    og: original
    nw: new
    """
    if og == 0:
        return 0

    x = round((nw - og) * 100 / og, rounding)

    return x if x < 100 else 100


def check_date_format(date: str) -> str:
    try:
        dt.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        raise InvalidDateFormat(
            "Invalid date format, please ensure that your format is %Y-%m-%d"
        )
