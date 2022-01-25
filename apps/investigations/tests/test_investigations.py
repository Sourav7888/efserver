from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from core.tests.utils import BaseTest
from core.models import UserInfo, Facility
from apps.investigations.models import Investigation
from apps.investigations.tasks import get_investigations_status


class InvestigationsTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)

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
        user_info = UserInfo.objects.get(user=user)
        user_info.access_investigation = True
        user_info.is_investigation_manager = True
        user_info.is_investigator = True

        user_info.save()

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
