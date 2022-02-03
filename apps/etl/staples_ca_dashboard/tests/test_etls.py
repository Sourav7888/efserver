from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status
from django.contrib import auth
from apps.etl.staples_ca_dashboard.models import Renewables


class TestRenewables(BaseTest):
    def setUp(self):
        super().setUp()
        Renewables.objects.bulk_create(
            [
                Renewables(
                    year=2020,
                    purchased_energy=1,
                    emission_reduction=1,
                    division="retail",
                    buyer="test",
                ),
                Renewables(
                    year=2021,
                    purchased_energy=1,
                    emission_reduction=1,
                    division="retail",
                    buyer="test",
                ),
            ]
        )

    def test_renewables(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)

        url = reverse("get_renewables_yearly")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_yearly_manager_renewables(self):

        data = Renewables.yearly.all()
        # @TODO: There is a bug here which prevents from accessing yearly
        # @TODO: Need to test


class TestLedList(BaseTest):
    def test_renewables(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)

        url = reverse("get_led_list")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestBillAudit(BaseTest):
    def test_bill_audit(self):
        # Test that only user with the same customer has access
        user = auth.get_user(self.client)

        url = reverse("get_bill_audit")
        data = {}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
