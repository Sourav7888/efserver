from apps.investigations.models import InvestigationAuthorization
from core.models import UserInfo, Customer
from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status
from django.contrib import auth


class ViewsTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        self.client.login(username="CoreTestUser", password="123")

    def test_get_generated_hc(self):

        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = auth.get_user(self.client)
        user.is_superuser = True
        user.save()

        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_generate_hc_by_facility(self):

    #     user = auth.get_user(self.client)
    #     UserInfo.objects.create(user=user)

    #     inv_auth = InvestigationAuthorization.objects.create(user_info=user.user_info)

    #     inv_auth.is_investigator = True
    #     inv_auth.access_investigation = True
    #     inv_auth.is_investigation_manager = True

    #     inv_auth.save()

    #     url = reverse("generate-hc-report-by-facility")
    #     response = self.client.get(
    #         url,
    #         data={
    #             "facility": "CoreFacilityName",
    #             "utility_type": "electricity",
    #             "investigation_date": "2020-01-01",
    #         },
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_hc_by_division(self):
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
