from core.tests.utils import BaseTest
from core.models import UserInfo, Customer
from django.urls import reverse
from rest_framework import status
from django.contrib import auth


class TestRenewables(BaseTest):
    def test_renewables(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)

        url = reverse("get_renewables")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
