from core.tests.utils import BaseTest
from core.models import UserInfo, Customer
from django.urls import reverse
from rest_framework import status
from django.contrib import auth


class ViewsTestCase(BaseTest):
    fixtures = ["EnergyFixture.json"]

    def test_get_division_utility(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)
        user_info = UserInfo.objects.create(user=user)

        url = reverse("get_division_utility")
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

        # Adding timeframe monthly to query
        response = self.client.get(url, {"timeframe": "monthly"} | data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(not response.json()["results"], False)

        # Testing Yearly query
        response = self.client.get(url, {"timeframe": "yearly"} | data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
