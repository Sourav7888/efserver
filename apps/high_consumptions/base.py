from abc import ABC, abstractmethod
from core.models import Facility
from django.template.loader import render_to_string
from datetime import datetime as dt
from typing import Any
from apps.utility_manager.queries import (
    query_facility_energy_weather,
    query_facility_specific_month_stats,
)
from .analytics.linear_regression import get_linear_regression_model
from .analytics.basics import calculate_col_avg
import pandas as pd
from apps.shared.parsers import parse_year_month
from .cs_exeptions import TargetDateNotFound, EmptyDataFrame


class HighConsumption(ABC):
    template = None  # High Consumption Document

    def __init__(self, facility: Facility, investigation_date: dt):
        self._facility = facility
        self._investigation_date = investigation_date
        self._context: dict[str, Any] = {}
        self._dataframe: pd.DataFrame = pd.DataFrame([])

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def context(self) -> dict[str, Any]:
        return self._context

    def additional_context(self):
        """
        Override to Add additional context to the template
        """
        pass

    def render_template(self, **kwargs) -> str:
        """
        Render the template based on the current context
        """
        if not self.template:
            raise NotImplementedError("Template is not defined! Unable to render")

        if kwargs:
            # Add any additional context to the context before rendering
            self.additional_context(**kwargs)

        # Render the template
        template = render_to_string(
            f"{self.template}", {"context": self._context}
        ).encode("utf-8")

        return template

    @classmethod
    def create_hc_by_facility_name(cls, facility: str, investigation_date: str):
        """
        Create an instance of the class by providing the facility name
        """
        try:
            investigation_date = dt.strptime(investigation_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format, should be YYYY-MM-DD")

        facility = Facility.objects.get(facility_name=facility)
        return cls(facility, investigation_date)

    @classmethod
    def create_hc_by_facility_obj(cls, facility: Facility, investigation_date: str):
        """
        Create an instance of the class by providing the facility object
        """
        try:
            investigation_date = dt.strptime(investigation_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format, should be YYYY-MM-DD")
        return cls(facility, investigation_date)

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """
        Get the data for the high consumption
        """
        pass

    @abstractmethod
    def check_dataframe(self) -> bool:
        """
        Check that runs before the method to ensure that the data
        has all the necessary attributes
        """
        pass

    @abstractmethod
    def run_method(self):
        """
        The analytics used for the high consumption
        Calling this method will update the context
        """
        pass

    @abstractmethod
    def is_hc(self) -> bool:
        """
        Returns a true or false by looking at the context
        """

    @abstractmethod
    def get_description(self) -> str:
        """
        Returns a description of the high consumption
        """


class GasHighConsumption(HighConsumption):
    """
    Class that handles Natural Gas high consumption
    """

    template = "hc_gas.html"

    def get_data(self, method: Any = query_facility_energy_weather) -> pd.DataFrame:
        """
        Get the data for the high consumption, method can be overriden
        """
        self._dataframe = method(self._facility, "NaturalGas")
        return self._dataframe

    def check_dataframe(self):
        """
        Check that runs before the method to ensure that the data
        has all the necessary attributes
        """
        if self._dataframe.empty:
            raise EmptyDataFrame("Dataframe is empty! Check not passed.")

        # Test if the investigation date is in the dataframe
        if self._dataframe[self._dataframe["date"] == self._investigation_date].empty:
            raise TargetDateNotFound(
                "Investigation date not in dataframe! Check not passed."
            )

    def _add_facility_context(self):
        """
        Add the facility context to the context
        """
        self._context["facility"] = {
            "facility_name": self._facility.facility_name,
            "address": self._facility.address,
            "area": self._facility.area,
            "category_tyoe": self._facility.category_type,
            "latitude": self._facility.latitude,
            "longitude": self._facility.longitude,
        }

    def _add_stats_context(self, method: Any = query_facility_specific_month_stats):
        """
        Add the stats context to the context
        """
        # Period -- 5year:
        period = parse_year_month(
            self._investigation_date.year, self._investigation_date.month, diff=60
        )

        # Additional stats
        stats = method(
            self._facility,
            period[1].month,
            min_year=period[0].year,
            max_year=period[1].year,
            include_weather=True,
            utility_type="NaturalGas",
        )

        stats_date = stats["date"].astype(str).tolist()
        stats_hdd = stats["hdd"].tolist()
        stats_usage = stats["usage"].tolist()

        self._context["stats"] = {
            "date": stats_date,
            "hdd": stats_hdd,
            "usage": stats_usage,
        }

        self._context["render"]["stats"] = list(zip(stats_date, stats_hdd, stats_usage))

    def additional_context(self, **kwargs):
        """
        Add additional context to the template
        """
        if kwargs.get("facility_context", None):
            self._add_facility_context()

        # We want to add energy stats to the context
        # We must inject the function to make this testable
        if kwargs.get("stats_context", None):
            if callable(kwargs["stats_context"]):
                self._add_stats_context(kwargs["stats_context"])
            else:
                self._add_stats_context()

    def run_method(self):
        """
        The analytics used for the high consumption
        Calling this method will update the context
        """
        if self._dataframe.empty:
            self.get_data()

        self.check_dataframe()
        # @NOTE QUICK FIX
        self._dataframe.drop(columns=["billing_days", "unit"], inplace=True)

        self._dataframe.dropna(inplace=True)

        target = self._dataframe[self._dataframe["date"] == self._investigation_date]
        usage = self._dataframe["usage"].to_numpy().reshape(-1, 1)
        hdd = self._dataframe["hdd"].to_numpy().reshape(-1, 1)

        if target.empty:
            raise TargetDateNotFound(
                "Investigation date not in dataframe -> @run_method"
            )

        # Get linear model
        model = get_linear_regression_model(
            hdd, usage, include_test=True, include_og=True
        )

        # Predict what should the current usage be
        prediction = round(model["model"].predict([target.hdd]).item(), 2)

        # remove model it is not needed - Not Json serializable
        del model["model"]

        # Diff between target and prediction
        diff = target.usage - prediction

        # Percentage difference
        percentage_diff = round(diff * 100 / prediction, 2)

        # calculating the estimated cost based on the cost of that target date
        estimated_cost = diff * target.cost / target.usage

        # Building context
        self._context = {
            "prediction": prediction,
            "usage_vs_prediction": round(diff.item(), 2),
            "percentage_diff": percentage_diff.item(),
            "target_date": self._investigation_date,
            "month_hdd": target.hdd.item(),
            "month_usage": target.usage.item(),
            "estimated_cost": round(estimated_cost.item(), 2),
            "model": model,
            "render": {  # Necessary to render template table
                "model": list(zip(model["x"], model["y"], model["y_test"])),
            },
        }

    def is_hc(self) -> bool:
        """
        Returns a true or false by looking at the context
        """
        if not self._context:
            raise ValueError("Context is empty! Unable to determine if hc or not!")

        # if at least a 25% increase
        if self._context["percentage_diff"] > 25:
            if self._context["estimated_cost"] > 150:
                return True

        return False

    def get_description(self) -> str:
        """
        Returns a description of the high consumption
        """
        return f"""Auto-generated High Consumption:\n\nThe facility {self._facility.facility_name} has been flagged for High Natural Gas usage.\nBased on a linear prediction there is a {self.context["percentage_diff"]} (%) increase at an estimated cost of ${self.context["estimated_cost"]}.
        """


class ElectricityHighConsumption(HighConsumption):
    """
    Electricity high consumption:
    method?
    """

    template = "hc_el.html"

    def get_data(
        self,
        method: Any = query_facility_energy_weather,
    ) -> pd.DataFrame:
        """
        Get the data for the high consumption, method can be overriden
        """
        self._dataframe = method(self._facility, "Electricity")

        return self._dataframe

    def check_dataframe(self):

        # Similar to NaturalGasHighConsumption
        if self._dataframe.empty:
            raise EmptyDataFrame("Dataframe is empty! Check not passed.")

        # Test if the investigation date is in the dataframe
        if self._dataframe[self._dataframe["date"] == self._investigation_date].empty:
            raise TargetDateNotFound(
                "Investigation date not in dataframe! Check not passed."
            )

    def fetch_stats(self) -> pd.DataFrame:
        """
        Filter the dataframe to only the month of the investigation date
        updates the context as well
        """
        stats = self._dataframe[
            self._dataframe["date"].dt.month == self._investigation_date.month
        ]

        stats_date = stats["date"].astype(str).tolist()
        stats_cdd = stats["cdd"].tolist()
        stats_usage = stats["usage"].tolist()

        self._context["stats"] = {
            "date": stats_date,
            "cdd": stats_cdd,
            "usage": stats_usage,
        }

        if not self._context.get("render", None):
            self._context["render"] = {}

        self._context["render"]["stats"] = list(zip(stats_date, stats_cdd, stats_usage))

        return stats

    def _add_facility_context(self):
        """
        Add the facility context to the context
        """
        self._context["facility"] = {
            "facility_name": self._facility.facility_name,
            "address": self._facility.address,
            "area": self._facility.area,
            "category_type": self._facility.category_type,
            "latitude": self._facility.latitude,
            "longitude": self._facility.longitude,
        }

    def additional_context(self, **kwargs):
        """
        Add additional context to the template
        """
        if kwargs.get("facility_context", None):
            self._add_facility_context()

        # Add additional stats should be in additional stats
        if not self._context:
            raise Exception("Warning! Context is empty! Unable to add additional stats")

        self.fetch_stats()

    # @TODO: Breakdown and test
    def run_method(self):
        if self._dataframe.empty:
            self.get_data()

        self.check_dataframe()

        # The current stats
        target = self._dataframe[self._dataframe["date"] == self._investigation_date]

        # Dataframe including specific months
        stats = self._dataframe[
            self._dataframe["date"].dt.month == self._investigation_date.month
        ]

        # Add a unit cost to dataframe
        self._dataframe.loc[self._dataframe["usage"] > 0.0, "unit_cost"] = (
            self._dataframe["cost"] / self._dataframe["usage"]
        )

        # Exclude the target year when calculating the average
        avg_stats = stats[stats["date"].dt.year < self._investigation_date.year]

        # Calculate average
        average = calculate_col_avg(avg_stats, "usage")
        
        if not average:
            return
        
        # Calculate unit cost
        average_unit_cost = calculate_col_avg(self._dataframe, "unit_cost")
        # Calculate diff
        diff = target["usage"].item() - average

        # Percentage difference
        percentage_diff = round(diff * 100 / average, 2)

        # Calculate estimated hc cost
        estimated_cost = round(diff * average_unit_cost, 2)

        # Dataframe for usage / area
        u_a = self.dataframe["usage"] / self._facility.area

        # Calculate rolling usage/sqft
        usage_area = (
            (u_a.rolling(12).sum()[self._dataframe["date"] == self._investigation_date])
            .round(2)
            .item()
        )

        self._context = {
            "target_date": self._investigation_date,
            "month_cdd": target.cdd.item(),
            "month_usage": target.usage.item(),
            "average": average,
            "estimated_cost": estimated_cost,
            "percentage_diff": percentage_diff,
            "usage_area": usage_area,
            "usage_vs_prediction": round(target.usage.item() - average, 2),
        }

        if not self._context.get("render", None):
            self._context["render"] = {}

        self._context["render"]["avg"] = [average for _ in range(len(stats))]

    def is_hc(self) -> bool:
        if self._context["percentage_diff"] > 15:
            return True

        return False

    def get_description(self) -> str:
        return f"""Auto-generated High Consumption:\n\nThe facility {self._facility.facility_name} has been flagged for High Electricity usage as of {self._investigation_date.month}-{self._investigation_date.year}.\n Please investigate.
        """
