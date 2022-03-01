from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status


class ApiDocsTestCase(BaseTest):
    def test_staples_ca(self):
        url = reverse("get-staples-swagger-schema")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
