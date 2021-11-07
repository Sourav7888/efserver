from apps.utility_manager.parsers import UtilityBillPr
import pandas as pd
from pandas._testing import assert_frame_equal
from datetime import datetime as dt
from rest_framework.test import APITestCase


class TestUtilityBillParsers(APITestCase):
    parser = UtilityBillPr()

    def test_transform_df(self):
        in_1 = self.parser.transform_df(
            pd.DataFrame(
                [
                    {
                        "id": 1,
                        "billing_date": "2020-02-01",
                        "cost": 100,
                        "usage": 50,
                    },
                    {
                        "id": 2,
                        "billing_date": "2020-03-01",
                        "cost": 150,
                        "usage": 50,
                    },
                ]
            )
        )

        # Test Wrong key
        in_2 = self.parser.transform_df(
            pd.DataFrame(
                [
                    {
                        "id": 1,
                        "billing_date": "2020-02-01",
                        "cost": 100,
                        "consumption": 50,
                    },
                ]
            )
        )

        assert_frame_equal(
            in_1,
            pd.DataFrame(
                [
                    [dt.strptime("2020-02-01", "%Y-%m-%d"), 100, 50],
                    [dt.strptime("2020-03-01", "%Y-%m-%d"), 150, 50],
                ],
                columns=["billing_date", "cost", "usage"],
            ),
            check_dtype=False,
        )

        assert_frame_equal(
            in_2,
            pd.DataFrame(
                [],
            ),
            check_dtype=False,
        )
