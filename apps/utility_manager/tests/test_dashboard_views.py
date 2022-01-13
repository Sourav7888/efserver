from core.tests.utils import BaseTest
from core.models import UserInfo, Customer
from django.urls import reverse
from rest_framework import status
from django.contrib import auth


class ViewsTestCase(BaseTest):
    fixtures = ["EnergyFixture.json"]

    def test_get_division_energy_reduction(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)
        user_info = UserInfo.objects.create(user=user)

        url = reverse("calculate_total_energy_reduction")
        data = {
            "utility_type": "Electricity",
            "division_name": "FixtureDivision",
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Modify the user customer
        customer = Customer.objects.get(customer_name="FixtureCompany")
        user_info.customer = customer
        user_info.save()

        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_division_energy_average(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)
        user_info = UserInfo.objects.create(user=user)

        url = reverse("energy_division_ghg_pf")
        data = {
            "utility_type": "Electricity",
            "division_name": "FixtureDivision",
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Modify the user customer
        customer = Customer.objects.get(customer_name="FixtureCompany")
        user_info.customer = customer
        user_info.save()

        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
