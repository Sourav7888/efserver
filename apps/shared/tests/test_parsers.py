from shared.parsers import parse_month_year, parse_in_memory_csv
from datetime import datetime as dt
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from shared.parsers import parse_in_memory_csv


class TestParsers(APITestCase):
    def test_parse_month_year(self):
        # Test that month and year is corretly parsed
        expected = dt(2020, 1, 1)

        self.assertEqual(expected, parse_month_year(2020, 1))

        expected = (dt(2019, 2, 1), dt(2020, 1, 1))

        self.assertEqual(expected, parse_month_year(2020, 1, diff=12))

        # Invalid request
        self.assertEqual(None, parse_month_year(2020, 30))

    def test_parse_in_memory_csv(self):
        file = SimpleUploadedFile(
            "csv_file.csv",
            "2015-01-01,SBD0107,Electricity,2816.09,30240".encode("utf-8"),
        )

        self.assertEqual(
            parse_in_memory_csv(file),
            [
                [
                    "2015-01-01",
                    "SBD0107",
                    "Electricity",
                    "2816.09",
                    "30240",
                ]
            ],
        )
