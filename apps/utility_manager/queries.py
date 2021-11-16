from .parsers import UtilityBillPr
from apps.weather_manager.queries import (
    query_coord_weather_data,
    query_coord_specific_month_weather_data,
)
from django.db import models
from datetime import datetime as dt
import pandas as pd
from .models import UtilityBill
from typing import Any
from dateutil.relativedelta import relativedelta
from core.models import Facility


def query_facility_energy_as_dataframe(
    facility_obj: Facility, **kwargs
) -> pd.DataFrame:
    """
    Query facility energy as dataframe,
    kwargs can include all related to utility bill model
    """
    energy_parser = UtilityBillPr(
        queryset=UtilityBill.objects.filter(
            facility=facility_obj,
            **kwargs,
        )
        .select_related("facility")
        .order_by("billing_date")
    )
    energy = energy_parser.evaluate_queryset_to_df()
    return energy


def query_facility_specific_month_energy(
    facility_obj: models.Model,  # The facility object
    month: int,  # The month required
    min_year: int = None,  # The minimum year required,
    max_year: int = None,  # The maximum year required,
    **kwargs,
) -> pd.DataFrame:
    """
    Query the specific month energy usage for a facility
    including the same month of past year
    """
    if not min_year or not max_year:
        raise ValueError("min_year and max_year must be provided!")

    energy = query_facility_energy_as_dataframe(
        facility_obj,
        billing_date__month=month,
        billing_date__year__gte=min_year,
        billing_date__year__lte=max_year,
        **kwargs,
    )

    return energy


def query_facility_energy_weather(
    facility_obj: models.Model,
    utility_type: str,
    weather_method: callable = query_coord_weather_data,
    **kwargs,
) -> pd.DataFrame:
    """
    Query the facility energy data paired with its weather counterpart
    kwargs: filters related to the Utility bill model
    """

    # Query all facilility utility_type energy
    energy = query_facility_energy_as_dataframe(
        facility_obj, utility_type=utility_type, **kwargs
    )

    if not energy.empty:
        # get the max and min billing_date in energy dataframe
        max_billing_date = energy.billing_date.max()
        min_billing_date = energy.billing_date.min()

        # Weather data
        weather_data = weather_method(
            lat=facility_obj.latitude,
            lng=facility_obj.longitude,
            date__gte=min_billing_date,
            date__lt=max_billing_date
            + relativedelta(months=+1),  # This needs to be the full month value
        )
        # Merge to the energy dataframe
        merged = pd.merge(
            energy,
            weather_data,
            how="left",
            left_on="billing_date",
            right_on="date",
        )
        # drop billing_date col and final formatting
        merged.drop(["billing_date"], axis=1, inplace=True)

        return merged

    return pd.DataFrame([])


def query_facility_specific_month_stats(
    facility_obj: models.Model,  # The facility object
    month: int,  # The month required
    min_year: int = None,  # The minimum year required,
    max_year: int = None,  # The maximum year required,
    include_weather: bool = True,  # Include weather data
    weather_method: callable = query_coord_specific_month_weather_data,
    **kwargs,
) -> pd.DataFrame:

    if not min_year or not max_year:
        raise ValueError("min_year and max_year must be provided!")

    energy = query_facility_specific_month_energy(
        facility_obj, month, min_year=min_year, max_year=max_year, **kwargs
    )

    if not energy.empty:
        if include_weather:

            # Weather data
            weather_data = weather_method(
                facility_obj.latitude,
                facility_obj.longitude,
                month,
                min_year=min_year,  # required min_year
                max_year=max_year,  # required max_year
            )

            # Merge to the energy dataframe
            merged = pd.merge(
                energy,
                weather_data,
                how="left",
                left_on="billing_date",
                right_on="date",
            )
            # drop billing_date col and final formatting
            merged.drop(["billing_date"], axis=1, inplace=True)

            return merged

    return pd.DataFrame([])
