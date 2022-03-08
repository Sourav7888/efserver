import pandas as pd
from core.models import Division, Facility
from apps.utility_manager.models import UtilityBill
from apps.analytics.constants import (
    EPA_ELECTRICITY_GHG_MULTIPLIER,
    EPA_NATURALGAS_MULTIPLIER,
    GJ_TO_THERMS,
)
from apps.utility_manager.queries import query_avg_division_usage_per_month_per_facility
from abc import ABC, abstractmethod
from datetime import datetime as dt
import json


class ScoreCard(ABC):
    """
    Base class for scorecard
    """

    @abstractmethod
    def avg_facility_usg_per_month(self):
        ...

    @abstractmethod
    def month_performance(self):
        ...

    @abstractmethod
    def yearly_consumptions(self):
        ...


class ScoreCardQ(ScoreCard):

    """
    This is the main implementation of the scorecard
    has yearly consumption
    has facility consumption average per month
    has monthly performance for a specified month

    This will return query version somewhat messy its best to use ScoreCardDf

    """

    def __init__(self, division_name: str):
        self._division = self._division_obj(division_name)
        self._facilities = self._facilities_obj()

    def _division_obj(self, division_name: str):
        """
        Returns the division object
        """
        return Division.objects.get(division_name=division_name)

    def _facilities_obj(self):
        """
        Query related facilities
        """
        return Facility.objects.filter(division=self._division)

    def avg_facility_usg_per_month(self, **kwargs):
        """
        Average Consumption per facility
        Include the emmission
        """
        data = {}
        queries = dict(
            electricity=query_avg_division_usage_per_month_per_facility(
                facilities=self._facilities, utility_type="Electricity", **kwargs
            ),
            natural_gas=query_avg_division_usage_per_month_per_facility(
                facilities=self._facilities, utility_type="NaturalGas", **kwargs
            ),
        )
        for k in queries:
            data[k] = self._add_emmission(queries[k], k, col="avg_usage")

        return data

    def month_performance(self, month: int, year: int):
        """
        Performance for a specific month compared to past months
        """
        # For consistency we will separate into two queries
        queries = dict(
            electricity=list(
                UtilityBill.monthly.filter(
                    facility__in=self._facilities,
                    billing_date__month=month,
                    billing_date__year__lte=year,
                    utility_type="Electricity",
                )
            ),
            natural_gas=list(
                UtilityBill.monthly.filter(
                    facility__in=self._facilities,
                    billing_date__month=month,
                    billing_date__year__lte=year,
                    utility_type="NaturalGas",
                )
            ),
        )

        data = {}
        for k in queries:
            data[k] = self._add_emmission(queries[k], k)

        return data

    def _add_emmission(self, query: dict, utility_type: str, col: str = "usage"):
        """
        Add ghg emission to the dict
        """

        cst = (
            EPA_ELECTRICITY_GHG_MULTIPLIER
            if utility_type == "electricity"
            else EPA_NATURALGAS_MULTIPLIER * GJ_TO_THERMS
        )
        return [{"ghg (MT)": float(x[col]) * cst, **x} for x in query]

    def yearly_consumptions(self) -> dict[str, dict]:
        """
        Monthly Consumption
        Including greenhouse
        """

        data = {}
        queries = dict(
            electricity=UtilityBill.yearly.filter(
                facility__in=self._facilities, utility_type="Electricity"
            ),
            natural_gas=UtilityBill.yearly.filter(
                facility__in=self._facilities, utility_type="NaturalGas"
            ),
        )

        for k in queries:
            data[k] = self._add_emmission(queries[k], k)

        return data


class ScoreCardDf(ScoreCardQ):
    """
    Subclass that will mainly returns the scorecard datas as dataframes
    or dict but its processed and curated
    """

    def __init__(self, division_name: str, json_safe: bool = False):
        super().__init__(division_name)
        self.json_safe = json_safe

    def _as_df(self, data: dict, rounding: int = 2) -> pd.DataFrame:
        """
        Merge the dataframes electricity and gas
        """
        dfs = pd.concat([pd.DataFrame(data[k]) for k in data])
        dfs.reset_index(drop=True, inplace=True)
        return dfs.round(rounding)

    def _as_json(self, df: pd.DataFrame) -> dict:
        """
        Return dataframe as json
        """
        return json.loads(df.to_json(None, orient="records"))

    def _merge_billing_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Some queries has month separated as billing_date__month or __year etc...
        merge those into one str date type
        """
        df["date"] = (
            "1-"
            + df["billing_date__month"].astype(str)
            + "-"
            + df["billing_date__year"].astype(str)
        )
        df.drop(columns=["billing_date__month", "billing_date__year"], inplace=True)
        df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%d-%m-%Y")).astype(str)
        df.sort_values(by="date", inplace=True)

        return df if not self.json_safe else self._as_json(df)

    def avg_facility_usg_per_month(self, **kwargs) -> pd.DataFrame:

        df = self._as_df(super().avg_facility_usg_per_month())

        # We need to format the date and sort for simplicity of use later on
        if not df.empty:
            self._merge_billing_date(df)

        return df if not self.json_safe else self._as_json(df)

    def yearly_consumptions(self) -> pd.DataFrame:
        df = self._as_df(super().yearly_consumptions())

        # We need to only keep the integer value of year
        # And then sort values
        if not df.empty:
            df["year"] = df["year"].apply(lambda x: x.year)
            df.sort_values(by=["year"], inplace=True)

        return df if not self.json_safe else self._as_json(df)

    def month_performance(self, month: int, year: int) -> pd.DataFrame:
        df = self._as_df(super().month_performance(month, year))
        if not df.empty:
            self._merge_billing_date(df)

        return df if not self.json_safe else self._as_json(df)


def generate_scorecard(division_name: str, month: int, year: int):
    """
    Generate a json file in memory file
    """
    scorecard = ScoreCardDf(division_name, json_safe=True)
    data = {
        "yearly_consumptions": scorecard.yearly_consumptions(),
        "avg_facility_usg_per_month": scorecard.avg_facility_usg_per_month(),
        "month_performance": scorecard.month_performance(month, year),
    }

    return data
