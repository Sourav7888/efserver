from core.models import Division, Facility
from core.tests.utils import BaseTest
from apps.utility_manager.queries import (
    query_facility_energy_as_dataframe,
    query_facility_specific_month_energy,
    query_facility_energy_weather,
    query_facility_specific_month_stats,
    query_avg_division_usage_per_month_per_facility,
)
import pandas as pd
from datetime import datetime as dt


def mock_weather_method(*args, **kwargs):
    df = pd.DataFrame(
        [
            {"date": "2019-01-01", "hdd": 1},
            {"date": "2019-02-01", "hdd": 2},
            {"date": "2019-03-01", "hdd": 3},
            {"date": "2019-04-01", "hdd": 4},
            {"date": "2019-05-01", "hdd": 5},
            {"date": "2019-06-01", "hdd": 6},
            {"date": "2019-07-01", "hdd": 7},
            {"date": "2019-08-01", "hdd": 8},
            {"date": "2019-09-01", "hdd": 9},
            {"date": "2019-10-01", "hdd": 10},
            {"date": "2019-11-01", "hdd": 11},
            {"date": "2019-12-01", "hdd": 12},
        ]
    )
    df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%Y-%m-%d"))
    return df


def mock_weather_method_2(*args, **kwargs):
    df = pd.DataFrame(
        [
            {"date": "2018-01-01", "hdd": 1},
            {"date": "2019-01-01", "hdd": 2},
        ]
    )
    df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%Y-%m-%d"))
    return df


class QueriesTestCase(BaseTest):
    fixtures = ["EnergyFixture.json"]

    def test_fixture(self):
        """
        test that the fixture is properly loaded
        """
        self.assertEqual(
            Facility.objects.filter(facility_name="FixtureFacility1").exists(), True
        )

    def test_facility_energy_as_dataframe(self):
        """
        Test that the facility energy is queried and returned as a dataframe
        """
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        df = query_facility_energy_as_dataframe(
            facility, utility_type="Electricity", billing_date__year=2019
        )

        self.assertEqual(isinstance(df, pd.DataFrame), True)
        self.assertEqual(len(df), 12)

    def test_specific_month_energy(self):
        """
        Test that the specific month energy is queried including same month of past years
        """
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        df = query_facility_specific_month_energy(
            facility, 12, min_year=2015, max_year=2020, utility_type="Electricity"
        )

        self.assertEqual(len(df), 6)

    def test_facility_energy_weather(self):
        """
        Test that the facility energy is queried and returned as a dataframe
        """
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        df = query_facility_energy_weather(
            facility,
            "Electricity",
            weather_method=mock_weather_method,
            billing_date__year=2019,
        )

        # Should be 12 data for a year
        self.assertEqual(len(df), 12)
        # Merged correctly
        self.assertEqual("hdd" in df.columns, True)
        self.assertEqual(int(df[df["date"] == dt(2019, 1, 1)].hdd), 1)

    def test_query_facility_specific_month_stats(self):
        """
        Test that the facility energy is queried and returned as a dataframe
        """
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        df = query_facility_specific_month_stats(
            facility,
            1,
            min_year=2018,
            max_year=2019,
            utility_type="Electricity",
            weather_method=mock_weather_method_2,
        )

        self.assertEqual(len(df), 2)
        # Merged correctly
        self.assertEqual("hdd" in df.columns, True)
        self.assertEqual(int(df[df["date"] == dt(2019, 1, 1)].hdd), 2)

    def test_avg_division_usage_per_month(self):
        division = Division.objects.get(division_name="FixtureDivision")
        facilities = Facility.objects.filter(division=division)
        avg = query_avg_division_usage_per_month_per_facility(facilities, "Electricity")

        self.assertEqual(
            float(avg[0]["avg_usage"]), (23580.000 + 30240.000) / 2
        )  # 26910
