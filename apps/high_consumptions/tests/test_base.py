from apps.utility_manager.models import UtilityBill
from core.models import Facility
from core.tests.utils import BaseTest
from apps.high_consumptions.base import GasHighConsumption
import pandas as pd
from datetime import datetime as dt
from apps.high_consumptions.cs_exeptions import EmptyDataFrame


def dummy_data(*args) -> pd.DataFrame:
    """
    Dummy data for testing
    """
    df = pd.read_csv("apps/high_consumptions/fixtures/EnergyWeather.csv")
    df["date"] = df["date"].apply(lambda x: dt.strptime(str(x), "%Y-%m-%d"))
    return df


def dummy_context(*args, **kwargs) -> pd.DataFrame:
    """
    Dummy context for testing
    """
    df = pd.read_csv("apps/high_consumptions/fixtures/DummyStats.csv")
    df["date"] = df["date"].apply(lambda x: dt.strptime(str(x), "%Y-%m-%d"))
    return df


class BaseTestCase(BaseTest):
    fixtures = ["apps/utility_manager/fixtures/EnergyFixture.json"]

    def setUp(self):
        super().setUp()

    def test_fixture(self):
        """
        test that the fixture is properly loaded
        """
        self.assertEqual(
            Facility.objects.filter(facility_name="FixtureFacility1").exists(), True
        )

    def test_gas_high_consumption(self):
        """
        test that the gas high consumption is properly calculated"""

        # Test that instance is properly created by name string
        hc = GasHighConsumption.create_hc_by_facility_name(
            "FixtureFacility1", "2020-01-01"
        )
        self.assertEqual(isinstance(hc._facility, Facility), True)

        # Test that instance is properly created by facility object
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        hc = GasHighConsumption.create_hc_by_facility_name(facility, "2020-01-01")
        self.assertEqual(isinstance(hc._facility, Facility), True)

        # Test that exceptions is raised when dataframe is empty
        self.assertRaises(EmptyDataFrame, hc.check_dataframe)

        # Test that context is updated after the method run properly
        hc.get_data(method=dummy_data)
        hc.run_method()

        self.assertEqual(not hc.context, False)

        # test that on render the context return bytes but also add additional context
        template = hc.render_template(
            facility_context=True, stats_context=dummy_context
        )
        self.assertEqual(type(template), bytes)
        self.assertEqual("facility" in hc.context, True)
        self.assertEqual("stats" in hc.context, True)
        self.assertEqual("stats" in hc.context["render"], True)

        # Test that this is high consuming
        self.assertEqual(hc.is_hc(), True)
