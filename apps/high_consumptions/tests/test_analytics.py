from apps.high_consumptions.analytics.basics import calculate_col_avg
from django.test import TestCase
import pandas as pd


class TestAnalytics(TestCase):
    def test_calculate_col_avg(self):
        mock_df = pd.DataFrame({"val": [1, 2, 3, 4, 5]})
        self.assertEqual(calculate_col_avg(mock_df, "val"), 3.0)