from apps.high_consumptions.models import HCReportTracker, HC
from apps.investigations.models import Investigation
from apps.investigations.models import InvestigationAuthorization
from core.models import UserInfo, Customer
from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status
from django.contrib import auth
from core.models import Facility


class ViewsTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.client.login(username="CoreTestUser", password="123")

    def test_get_generated_hc(self):

        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)

        inv_auth = InvestigationAuthorization.objects.create(user_info=user.user_info)

        inv_auth.is_investigator = True
        inv_auth.access_investigation = True
        inv_auth.is_investigation_manager = True

        inv_auth.save()

        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_hc_by_facility(self):

        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)

        inv_auth = InvestigationAuthorization.objects.create(user_info=user.user_info)

        inv_auth.is_investigator = True
        inv_auth.access_investigation = True
        inv_auth.is_investigation_manager = True

        inv_auth.save()

        url = reverse("generate-hc-report-by-facility")
        response = self.client.get(
            url,
            data={
                "facility": "CoreFacilityName",
                "utility_type": "electricity",
                "investigation_date": "2020-01-01",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_hc_by_division(
        self,
    ):
        user = auth.get_user(self.client)

        customer = Customer.objects.get(customer_name="CoreCustomerName")

        user_info = UserInfo.objects.create(user=user, customer=customer)

        inv_auth = InvestigationAuthorization.objects.create(user_info=user_info)

        inv_auth.is_investigator = True
        inv_auth.access_investigation = True
        inv_auth.is_investigation_manager = True

        inv_auth.save()

        url = reverse("generate-hc-by-division")
        response = self.client.post(
            url,
            data={
                "division": "CoreDivisionName",
                "utility_type": "electricity",
                "investigation_date": "2020-01-01",
            },
        )

        _id = response.json()["id"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        hc_tracker = HCReportTracker.objects.filter(hc_report_id=_id)

        self.assertEqual(hc_tracker.exists(), True)

        self.assertEqual(hc_tracker[0].is_ready, True)

    def test_investigations_hc_generation(self):

        user = auth.get_user(self.client)
        user_info = UserInfo.objects.create(user=user)
        inv_auth = InvestigationAuthorization.objects.create(user_info=user_info)
        inv_auth.is_investigation_manager = True
        inv_auth.access_investigation = True
        inv_auth.is_investigator = True
        inv_auth.save()

        facility = Facility.objects.get(facility_name="CoreFacilityName")

        hc = HC.objects.create(
            facility=facility, utility_type="HC_WT", target_date="2021-01-01"
        )

        HCReportTracker.objects.create(hc_report_id=hc.hc_id)

        mock = {
            "hc_id": hc.hc_id,
            "facility": "CoreFacilityName",
            "investigation_date": "2021-01-01",
            "investigation_type": "HC_WT",
            "investigation_description": "",
        }

        url = reverse("create_investigation_by_hc")
        response = self.client.post(
            url,
            data=mock,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Investigation.objects.filter(
                investigation_id=response.json()["id"]
            ).exists(),
            True,
        )

        # Test Delete generated HC
        mock = {
            "hc_id": hc.hc_id,
        }

        url = reverse("delete_generated_hc")
        response = self.client.post(
            url,
            data=mock,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            HC.objects.filter(hc_id=hc.hc_id).exists(),
            False,
        )

        self.assertEqual(
            HCReportTracker.objects.filter(hc_report_id=hc.hc_id).exists(),
            False,
        )
