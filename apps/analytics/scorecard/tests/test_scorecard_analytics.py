from apps.analytics.scorecard.scorecard_analytics import (
    ScoreCardQ,
    generate_scorecard,
    ScoreCardDf,
)
from django.test import TestCase
from apps.utility_manager.models import UtilityBill
from core.models import Division, Facility
from django.db.models import Sum
from apps.analytics.constants import (
    EPA_ELECTRICITY_GHG_MULTIPLIER,
    EPA_NATURALGAS_MULTIPLIER,
    GJ_TO_THERMS,
)
import pandas as pd
from pandas.testing import assert_frame_equal


class ScoreCardTestCase(TestCase):
    fixtures = ["apps/utility_manager/fixtures/EnergyFixture.json"]

    def test_scorecard_q(self):
        # Test instances
        scorecard = ScoreCardQ("FixtureDivision")
        self.assertEqual(isinstance(scorecard._division, Division), True)
        self.assertEqual(isinstance(scorecard._facilities[0], Facility), True)

        yearly = scorecard.yearly_consumptions()

        # Electricity
        expected_total = (
            UtilityBill.objects.filter(
                facility__in=scorecard._facilities,
                billing_date__year=2015,
                utility_type="Electricity",
            )
            .values("utility_type")
            .aggregate(Sum("usage"))
        )

        self.assertEqual(
            expected_total["usage__sum"], yearly["electricity"][0]["usage"]
        )

        self.assertEqual(
            float(expected_total["usage__sum"]) * EPA_ELECTRICITY_GHG_MULTIPLIER,
            yearly["electricity"][0]["ghg (MT)"],
        )

        # Natural Gas
        expected_total = (
            UtilityBill.objects.filter(
                facility__in=scorecard._facilities,
                billing_date__year=2015,
                utility_type="NaturalGas",
            )
            .values("utility_type")
            .aggregate(Sum("usage"))
        )

        self.assertEqual(
            expected_total["usage__sum"], yearly["natural_gas"][0]["usage"]
        )

        self.assertEqual(
            float(expected_total["usage__sum"])
            * EPA_NATURALGAS_MULTIPLIER
            * GJ_TO_THERMS,
            yearly["natural_gas"][0]["ghg (MT)"],
        )

        # Test average emmission
        avg_emmission = scorecard.avg_facility_usg_per_month()

        self.assertEqual(float(avg_emmission["electricity"][0]["avg_usage"]), 26910.0)

        # Test month data

        month_data = scorecard.month_performance(1, 2020)
        self.assertEqual(
            float(month_data["electricity"][0]["usage"]), 30240.000 + 23580.000
        )

    def test_scorecard_df(self):
        scorecard = ScoreCardDf("FixtureDivision")
        # Test that all methods are an instance of dataframe
        # Usually unless major changes in logic testing values would be overkill
        self.assertEqual(
            isinstance(scorecard.yearly_consumptions(), pd.DataFrame), True
        )
        self.assertEqual(
            isinstance(scorecard.month_performance(1, 2020), pd.DataFrame), True
        )
        self.assertEqual(
            isinstance(scorecard.avg_facility_usg_per_month(), pd.DataFrame), True
        )

        scorecard = ScoreCardDf("FixtureDivision", json_safe=True)
        # Test that all methods are an instance of a list
        # Usually unless major changes in logic testing values would be overkill
        self.assertEqual(isinstance(scorecard.yearly_consumptions(), list), True)

    def test_generate_scorecard(self):
        generate_scorecard("FixtureDivision", 1, 2020)

    def test_scorecard_analytics_with_no_data(self):
        # Make sure no error is happening if there is no data

        UtilityBill.objects.all().delete()
        scorecard = ScoreCardQ("FixtureDivision")
        yearly = scorecard.yearly_consumptions()
        self.assertEqual(yearly["electricity"], [])
        avg_emmission = scorecard.avg_facility_usg_per_month()
        self.assertEqual(avg_emmission["electricity"], [])
        month_data = scorecard.month_performance(1, 2020)
        self.assertEqual(month_data["electricity"], [])

        scorecard = ScoreCardDf("FixtureDivision")
        df = pd.DataFrame([]).reset_index(drop=True)
        yearly = scorecard.yearly_consumptions()
        assert_frame_equal(yearly, df, check_dtype=False)
        avg_emmission = scorecard.avg_facility_usg_per_month()
        assert_frame_equal(avg_emmission, df)
        month_data = scorecard.month_performance(1, 2020)
        assert_frame_equal(month_data, df)
