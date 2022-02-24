from rest_framework import status
from django.urls import reverse
from django.contrib import auth
from apps.high_consumptions.models import HC, HCReportTracker
from core.tests.utils import BaseTest
from core.models import UserInfo, Facility
from apps.investigations.models import Investigation, InvestigationAuthorization
from apps.investigations.tasks import get_investigations_status
from apps.investigations.permissions import get_or_create_investigation_authorization


class InvestigationsTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)

    def test_get_or_create_investigation_authorization(self):
        user = auth.get_user(self.client)
        inv_auth = InvestigationAuthorization.objects.filter(user_info=user.user_info)

        self.assertEqual(inv_auth.exists(), False)

        get_or_create_investigation_authorization(user.user_info.user_unique_id)

        inv_auth = InvestigationAuthorization.objects.filter(user_info=user.user_info)
        self.assertEqual(inv_auth.exists(), True)

    def test_investigations(self):
        """
        Test that an investigation manager can create an investigation
        """
        url = reverse("create_investigation")
        response = self.client.post(
            url,
            data={},
        )

        # Test that the user require permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Giving the user the permission should allow
        user = auth.get_user(self.client)

        get_or_create_investigation_authorization(
            user.user_info.user_unique_id, as_dict=True
        )

        user_info = UserInfo.objects.get(user=user)
        inv_auth = InvestigationAuthorization.objects.get(user_info=user_info)
        inv_auth.is_investigation_manager = True
        inv_auth.access_investigation = True
        inv_auth.is_investigator = True
        inv_auth.save()

        response = self.client.post(
            url,
            data={
                "facility": "CoreFacilityName",
                "investigation_date": "2021-12-12",
                "investigation_type": "HC_WT",
                "investigation_description": "This is a HC Investigation",
            },
        )

        # Test that the user require permission
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        investigation = Investigation.objects.filter(
            investigation_id=response.json()["investigation_id"]
        )

        # ensure that the investigation is created
        self.assertEqual(
            True,
            investigation.exists(),
        )

        # Ensure that the user on investigation is the same as the creator
        self.assertEqual(
            str(investigation.first().investigation_creator.user.username), str(user)
        )

        # Test that when creating a duplicate fails
        response = self.client.post(
            url,
            data={
                "facility": "CoreFacilityName",
                "investigation_date": "2021-12-12",
                "investigation_type": "HC_WT",
                "investigation_description": "This is a HC Investigation",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test that you can update an investigation
        url = reverse(
            "update_investigation", args=(investigation.first().investigation_id,)
        )
        response = self.client.put(
            url,
            data={"investigation_result": "Test Description"},
        )

        self.assertEqual(response.json()["investigation_result"], "Test Description")

        # Send a patch request
        url = reverse(
            "update_investigation", args=(investigation.first().investigation_id,)
        )
        response = self.client.put(
            url,
            data={"closed": True},
        )

        self.assertEqual(response.json()["closed"], True)

        # Create investigations by HCs

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

    def test_get_investigations(self):
        """
        Test that the investigations are not empty
        """

        facility = Facility.objects.get(facility_name="CoreFacilityName")
        Investigation.objects.create(
            facility=facility,
            investigation_type="HC_WT",
            investigation_date="2021-12-12",
        )

        self.assertEqual(
            get_investigations_status(),
            {
                "total_investigations": 1,
                "closed_investigations": 0,
                "in_monitoring_investigations": 0,
                "open_investigations": 1,
                "on_going_investigations": 0,
            },
        )
