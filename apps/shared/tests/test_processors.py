from ..processors import (
    group_and_sum,
    convert_year_month_to_dt,
    calculate_diff,
    check_date_format,
    check_email_format,
)
from pandas._testing import assert_frame_equal
import pandas as pd
from datetime import datetime as dt
from ..cs_exceptions import InvalidDateFormat
from rest_framework.test import APITestCase


class TestProcessors(APITestCase):
    @staticmethod
    def in_group_and_sum():
        df = pd.DataFrame(
            [
                {"date": "2020-01-01", "val": 1},
                {"date": "2020-01-01", "val": 1},
                {"date": "2020-02-01", "val": 1},
                {"date": "2021-03-01", "val": 1},
                {"date": "2021-03-01", "val": 1},
            ]
        )
        df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%Y-%m-%d"))

        return df

    def test_group_sum(self):
        """
        Test that group and sum is working properly
        """

        _df = self.in_group_and_sum()

        df_year = group_and_sum(_df, year=True, group_by="date")
        df_month = group_and_sum(_df, month=True, group_by="date")
        df_both = group_and_sum(_df, year=True, month=True, group_by="date")

        assert_frame_equal(
            df_year,
            pd.DataFrame(
                [
                    {"year": 2020, "val": 3},
                    {"year": 2021, "val": 2},
                ]
            ).set_index("year"),
            check_dtype=False,
        )
        assert_frame_equal(
            df_month,
            pd.DataFrame(
                [
                    {"month": 1, "val": 2},
                    {"month": 2, "val": 1},
                    {"month": 3, "val": 2},
                ]
            ).set_index("month"),
            check_dtype=False,
        )
        assert_frame_equal(
            df_both,
            pd.DataFrame(
                [
                    {"year": 2020, "month": 1, "val": 2},
                    {"year": 2020, "month": 2, "val": 1},
                    {"year": 2021, "month": 3, "val": 2},
                ]
            ).set_index(["year", "month"]),
            check_dtype=False,
        )

    def test_convert_year_month_to_dt(self):
        df = pd.DataFrame([[2020, 1]], columns=["year", "month"])
        exp = pd.DataFrame([dt(2020, 1, 1)], columns=["date"])

        assert_frame_equal(convert_year_month_to_dt(df), exp, check_dtype=False)

    def test_calculate_diff(self):
        assert 50 == calculate_diff(10, 15)

        assert 0 == calculate_diff(0, 15)

        assert -100 == calculate_diff(15, 0)

    def test_check_date_format(self):

        self.assertRaises(InvalidDateFormat, check_date_format, "sajlkdsa")

        assert check_date_format("2020-01-01") == "2020-01-01"

    def test_check_email_format(self):
        self.assertEqual(check_email_format("asdsadsa"), False)
        self.assertEqual(check_email_format("asds.x@vak.ca"), True)
