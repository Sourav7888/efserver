from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status


class ReportsTestCase(BaseTest):
    def test_get_customer_reports(self):
        url = reverse("get_customer_reports")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
