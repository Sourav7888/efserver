from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from core.models import Division, Facility, FacilityAccessControl, Customer, UserInfo


class CoreTestCase(APITestCase):
    """
    Test the core permission as user usually has to request facility_name or division_name
    """

    data = {
        "user": {"username": "CoreTestUser", "password": "123"},
        "division": {"division_name": "CoreDivisionName"},
        "facility": {"facility_name": "CoreFacilityName"},
        "customer": {"customer_name": "CoreCustomerName"},
    }

    def setUp(self):
        customer = Customer.objects.create(**self.data["customer"])

        # User by default acces_level="RESTRICTED" and customer will be null
        user = User.objects.create_user(**self.data["user"])
        user_info = UserInfo.objects.create(user=user)

        # Division is associated with a customer
        division = Division.objects.create(**self.data["division"], customer=customer)
        facility = Facility.objects.create(**self.data["facility"], division=division)

        self.client.login(**self.data["user"])

    def test_permissions(self):
        # Testing that a user cannot access a division information unless
        # user is of the same customer

        def request():

            url = reverse("test_core_view")
            response = self.client.get(
                url,
                data={
                    "division_name": "CoreDivisionName",
                    "facility_name": "CoreFacilityName",
                },
            )

            return response

        self.assertEqual(request().status_code, status.HTTP_403_FORBIDDEN)

        # Change the user to the same customer and give all access because of the
        # Facility blocking
        customer = Customer.objects.get(customer_name="CoreCustomerName")
        user = User.objects.get(username="CoreTestUser")
        user_info = UserInfo.objects.get(user=user)
        user_info.customer = customer
        user_info.access_level = "ALL"
        user_info.save()

        self.assertEqual(request().status_code, status.HTTP_200_OK)

        # Return user to restric and test that it fails
        user_info.access_level = "RESTRICTED"
        user_info.save()
        self.assertEqual(request().status_code, status.HTTP_403_FORBIDDEN)

        # Adding the facility to the access control should now allow the request to pass
        # Through
        facility = Facility.objects.get(facility_name="CoreFacilityName")
        facility_access_control = FacilityAccessControl.objects.create(
            user=user, facility=facility
        )

        self.assertEqual(request().status_code, status.HTTP_200_OK)
