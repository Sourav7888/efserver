from rest_framework.test import APITestCase
import pandas as pd
from datetime import datetime as dt
from pandas._testing import assert_frame_equal
from apps.weather_manager.parsers import WeatherDataPr


class TestParsers(APITestCase):
    parser = WeatherDataPr()

    def in_transform_df(self):
        return pd.DataFrame(
            [
                {
                    "pk_id": 4,
                    "date": "2015-01-01",
                    "hdd": 17.9,
                    "cdd": 0,
                    "climate_id": "1017099",
                },
                {
                    "pk_id": 5,
                    "date": "2015-01-02",
                    "hdd": 16.5,
                    "cdd": 0,
                    "climate_id": "1017099",
                },
            ]
        )

    def out_transform_df(self):
        df = pd.DataFrame(
            [
                {"date": "2015-01-01", "hdd": 17.9, "cdd": 0, "climate_id": "1017099"},
                {"date": "2015-01-02", "hdd": 16.5, "cdd": 0, "climate_id": "1017099"},
            ]
        )
        df["date"] = df["date"].apply(
            lambda x: dt.strptime(x, "%Y-%m-%d")
        )  # pandas still checks date types
        return df

    def test_transform_df(self):
        assert_frame_equal(
            self.out_transform_df(),
            self.parser.transform_df(self.in_transform_df()),
            check_dtype=False,
        )
