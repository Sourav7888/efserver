from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from core.models import Division, Facility, FacilityAccessControl, Customer, UserInfo
from tests.utils import BaseTest


class CoreTestCase(BaseTest):
    """
    Test the core permission as user usually has to request facility_name or division_name
    """

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

        # Checking that a user_info is automatically created
        # When auth0 calls it only creates a user in django User
        user = User.objects.get(username="CoreTestUser")
        # First we ensure this is false
        self.assertEqual(hasattr(user, "user_info"), False)

        # Test that the request is denied but the user info is created regardless
        self.assertEqual(request().status_code, status.HTTP_403_FORBIDDEN)
        user = User.objects.get(username="CoreTestUser")
        self.assertEqual(hasattr(user, "user_info"), True)

        # Change the user to the same customer and give all access because of the
        # Facility blocking
        customer = Customer.objects.get(customer_name="CoreCustomerName")
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

    def test_division_list(self):
        """
        Test that a user can get the division list associated with its customer base
        """
        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)
        url = reverse("get_division_list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test that only customers of the same base is included
        # In this case the user is assigned to None customer
        self.assertEqual(1, len(response.json()["results"]))
        self.assertEqual(
            None,
            response.json()["results"][0]["customer"],
        )

    def test_facility_list(self):
        """
        Test getting the list of facilities and its permissions
        """
        # Test that if a user is on RESTRICTED access the control access is used
        user = auth.get_user(self.client)
        UserInfo.objects.create(user=user)
        division = Division.objects.get(division_name="CoreDivisionName")
        facility = Facility.objects.get(facility_name="CoreFacilityName")

        # Test that response is empty the facility being in access control
        url = reverse("get_facility_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.json()["results"]))

        # Create a dummy facility that is in the same division
        # And test that only facilities in access control are returned
        facility2 = Facility.objects.create(
            facility_name="CoreFacilityName2", division=division
        )

        access_control = FacilityAccessControl.objects.create(
            user=user, facility=facility2
        )
        url = reverse("get_facility_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.json()["results"]))

        # Test that all access user has access to all facilities
        # with the same division
        user = User.objects.get(username="CoreTestUser")
        user_info = UserInfo.objects.get(user=user)
        user_info.customer = Customer.objects.get(customer_name="CoreCustomerName")
        user_info.access_level = "ALL"
        user_info.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create another dummy facility to test that facilities not associated with
        # the same customer does not show up
        facility3 = Facility.objects.create(facility_name="CoreFacilityName3")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.json()["results"]))
