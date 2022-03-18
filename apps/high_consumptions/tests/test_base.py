from core.models import Facility
from core.tests.utils import BaseTest
from apps.high_consumptions.base import GasHighConsumption, ElectricityHighConsumption
import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime as dt
from apps.high_consumptions.cs_exeptions import EmptyDataFrame
from apps.high_consumptions.tasks import create_hc_investigation
from apps.investigations.models import Investigation


def dummy_data(*args) -> pd.DataFrame:
    """
    Dummy data for testing
    """
    df = pd.read_csv("apps/high_consumptions/fixtures/EnergyWeather.csv")
    df["date"] = df["date"].apply(lambda x: dt.strptime(str(x), "%Y-%m-%d"))
    # df.drop(columns=["billing_days"], inplace=True)
    return df


def dummy_context(*args, **kwargs) -> pd.DataFrame:
    """
    Dummy context for testing
    """
    df = pd.read_csv("apps/high_consumptions/fixtures/DummyStats.csv")
    df["date"] = df["date"].apply(lambda x: dt.strptime(str(x), "%Y-%m-%d"))
    # df.drop(columns=["billing_days"], inplace=True)
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

        # Test that creating an investigation work correctly
        investigation_id = create_hc_investigation(
            facility,
            template,
            "HC_GAS",
            "2020-01-01",
            hc.get_description(),
            include_document=False,
        )

        self.assertEqual(
            Investigation.objects.filter(investigation_id=investigation_id).exists(),
            True,
        )

    def test_electricity_high_consumption(self) -> None:
        """
        Test electricity high consumption process
        """
        # Test that instance is properly created by name string
        hc = ElectricityHighConsumption.create_hc_by_facility_name(
            "FixtureFacility1", "2020-01-01"
        )
        self.assertEqual(isinstance(hc._facility, Facility), True)

        # Test that instance is properly created by facility object
        facility = Facility.objects.get(facility_name="FixtureFacility1")
        hc = ElectricityHighConsumption.create_hc_by_facility_name(
            facility, "2020-01-01"
        )
        self.assertEqual(isinstance(hc._facility, Facility), True)

        # Test that exceptions is raised when dataframe is empty
        self.assertRaises(EmptyDataFrame, hc.check_dataframe)

        # Test that context is updated after the method run properly
        hc.get_data(method=dummy_data)
        hc.run_method()
        stats = hc.fetch_stats()
        _context = dummy_context()

        # Some column manipulation necessary to pass the test
        stats.reset_index(inplace=True)
        stats = stats.drop(columns=["Unnamed: 0", "index", "unit_cost"], axis=1)
        _context = _context.drop(columns=["Unnamed: 0"], axis=1)

        assert_frame_equal(stats, _context, check_dtype=False, check_index_type=False)

        self.assertEqual(hc.is_hc(), False)

        # test that on render the context return bytes but also add additional context
        template = hc.render_template(facility_context=True)

        with open("apps/high_consumptions/tests/test_render.html", "wb") as f:
            f.write(template)
