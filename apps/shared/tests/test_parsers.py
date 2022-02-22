from ..parsers import parse_year_month, parse_in_memory_csv
from datetime import datetime as dt
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..parsers import parse_in_memory_csv, list_to_odr_list


class TestParsers(APITestCase):
    def test_parse_year_month(self):
        # Test that month and year is corretly parsed
        expected = dt(2020, 1, 1)

        self.assertEqual(expected, parse_year_month(2020, 1))

        expected = (dt(2019, 2, 1), dt(2020, 1, 1))

        self.assertEqual(expected, parse_year_month(2020, 1, diff=12))

        # Invalid request
        self.assertEqual(None, parse_year_month(2020, 30))

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

    def test_list_to_odr_list(self):
        mock = [["a", "b", "c"], [1, 2, 3]]
        result = list_to_odr_list(mock, ["c", "b", "a"])
        self.assertEqual(result, [[3, 2, 1]])
