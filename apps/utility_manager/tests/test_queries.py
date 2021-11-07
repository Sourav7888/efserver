from apps.utility_manager.models import UtilityBill
from core.models import Facility
from core.tests.utils import BaseTest
from apps.utility_manager.queries import (
    query_facility_energy_as_dataframe,
    query_facility_specific_month_energy,
)
import pandas as pd


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
