from core.tests.utils import BaseTest
from apps.etl.waste_manager.models import WasteData, WasteCategory, WasteProvider
from apps.etl.waste_manager.etl import bulk_create_waste_data
from core.models import Facility

from django.urls import reverse
from rest_framework import status


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
            ],
            [
                "2020-04-01",
                "CoreFacilityName",
                "Test",
                "10",
                "true",
                "TestCategory",
                "TestWasteProvider",
            ],
        ]
        # Test Create
        bulk_create_waste_data(data)

        facility = Facility.objects.get(facility_name="CoreFacilityName")

        waste = WasteData.objects.get(facility=facility, pickup_date="2020-01-01")

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
            ],
        ]

        # # Test Update

        bulk_create_waste_data(update)
        waste = WasteData.objects.get(facility=facility, pickup_date="2020-01-01")

        self.assertEqual(int(waste.weight), 15)

        # Test the yearly manager
        yearly = WasteData.yearly.all()

        self.assertEqual(int(yearly[0]["weight"]), 25)

    def test_yearly_view(self):
        url = reverse("get_waste_data_yearly")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("get_waste_data")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
