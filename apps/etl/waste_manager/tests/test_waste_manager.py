from core.tests.utils import BaseTest
from apps.etl.waste_manager.models import WasteData, WasteCategory, WasteProvider
from apps.etl.waste_manager.etl import bulk_create_waste_data
from core.models import Facility

from django.urls import reverse
from rest_framework import status
from django.contrib import auth
from core.models import UserInfo, Customer


class ETLTestCase(BaseTest):
    def test_etl(self):

        WasteCategory.objects.create(category_name="TestCategory")
        WasteProvider.objects.create(provider_name="TestWasteProvider")

        # (pickup_date, facility, waste_name, weight, is_recycled, waste_category, provided_by)
        data = [  # normal data
            [
                "2020-01-01",
                "CoreFacilityName",
                "Test",
                "10",
                "true",
                "TestCategory",
                "TestWasteProvider",
                "false",
                "mt",
            ],
            [
                "2020-04-01",
                "CoreFacilityName",
                "Test",
                "10",
                "true",
                "TestCategory",
                "TestWasteProvider",
                "false",
                "mt",
            ],
            [
                "2020-04-03",
                "CoreFacilityName",
                "Test",
                "15",
                "true",
                "TestCategory",
                "TestWasteProvider",
                "false",
                "mt",
            ],
            [
                "2020-01-01",
                "CoreFacilityName",
                "Test",
                "15",
                "false",
                "TestCategory",
                "TestWasteProvider",
                "false",
                "mt",
            ],
        ]
        # Test Create
        bulk_create_waste_data(data)

        facility = Facility.objects.get(facility_name="CoreFacilityName")

        waste = WasteData.objects.get(
            facility=facility, pickup_date="2020-01-01", is_recycled=True
        )

        self.assertEqual(int(waste.weight), 10)

        update = [  # normal data
            [
                "2020-01-01",
                "CoreFacilityName",
                "Test",
                "15",
                "true",
                "TestCategory",
                "TestWasteProvider",
                "false",
                "mt",
            ],
        ]

        # # Test Update
        bulk_create_waste_data(update)
        waste = WasteData.objects.get(
            facility=facility, pickup_date="2020-01-01", is_recycled=True
        )
        self.assertEqual(int(waste.weight), 15)

        # Test the yearly manager
        yearly = WasteData.yearly.all()

        self.assertEqual(int(yearly[0]["weight"]), 15)
        self.assertEqual(int(yearly[0]["is_recycled"]), False)

        self.assertEqual(int(yearly[1]["weight"]), 40)
        self.assertEqual(int(yearly[1]["is_recycled"]), True)

        # Test monthly manager
        monthly = WasteData.monthly.all()

        self.assertEqual(int(monthly[1]["weight"]), 25)

    def test_views(self):
        user = auth.get_user(self.client)
        user_info = UserInfo.objects.create(user=user)

        customer = Customer.objects.get(customer_name="CoreCustomerName")
        user_info.customer = customer
        user_info.save()

        # Yearly
        url = reverse("get_waste_data_yearly")
        data = {"division": "CoreDivisionName"}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Monthly
        url = reverse("get_waste_data")
        data = {"division": "CoreDivisionName"}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Total
        url = reverse("get_waste_data_total")
        data = {
            "division": "CoreDivisionName",
            "waste_category": "TestCategory",
            "min_date": "2020-01-01",
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Recycling rate
        url = reverse("get_waste_recycling_rate")
        data = {"division": "CoreDivisionName", "waste_category": "TestCategory"}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Contribution by name
        url = reverse("get_waste_contribution_by_name")
        data = {
            "division": "CoreDivisionName",
            "waste_category": "TestCategory",
            "year": 2020,
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Contribution by name
        url = reverse("get_waste_data_total_all_category")
        data = {
            "unit": "kg",
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
