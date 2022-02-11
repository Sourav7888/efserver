from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from core.models import (
    Division,
    Facility,
    FacilityAccessControl,
    Customer,
    UserInfo,
    PreAuthorizedUser,
)
from core.tests.utils import BaseTest
from core.etl import bulk_create_facility


class CoreTestCase(BaseTest):
    """
    Test the core permission as user usually has to request facility_name or division_name
    """

    def test_permissions(self):
        # Testing that a user cannot access a division information unless
        # user is of the same customer

        def get_request(
            data={
                "division_name": "CoreDivisionName",
                "facility_name": "CoreFacilityName",
            }
        ):

            url = reverse("test_core_view")
            response = self.client.get(
                url,
                data=data,
            )

            return response

        def post_request(
            data={
                "division_name": "CoreDivisionName",
                "facility_name": "CoreFacilityName",
            }
        ):
            url = reverse("test_core_view")
            response = self.client.post(
                url,
                data=data,
            )

            return response

        # Checking that a user_info is automatically created
        # When auth0 calls it only creates a user in django User
        user = User.objects.get(username="CoreTestUser")
        # First we ensure this is false
        self.assertEqual(hasattr(user, "user_info"), False)

        # Test that the request is denied but the user info is created regardless
        # This is due to the CheckRequestBody
        # Test that query strings are checked
        get_response = get_request()
        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)
        assert (
            get_response.request["QUERY_STRING"]
            == "division_name=CoreDivisionName&facility_name=CoreFacilityName"
        )
        # Test Post should be refused also
        # Test that multipart and body are checked
        post_response = post_request()
        self.assertEqual(post_response.status_code, status.HTTP_403_FORBIDDEN)
        # Not using query string
        assert post_response.request["QUERY_STRING"] == ""

        # Is using body / wsgi
        assert (
            post_response.wsgi_request.POST.get("division_name") == "CoreDivisionName"
        )

        user = User.objects.get(username="CoreTestUser")
        self.assertEqual(hasattr(user, "user_info"), True)

        # Change the user to the same customer and give all access because of the
        # Facility blocking
        customer = Customer.objects.get(customer_name="CoreCustomerName")
        user_info = UserInfo.objects.get(user=user)
        user_info.customer = customer
        user_info.access_level = "ALL"
        user_info.save()

        self.assertEqual(get_request().status_code, status.HTTP_200_OK)

        self.assertEqual(post_request().status_code, status.HTTP_200_OK)

        # Return user to restrict and test that it fails
        user_info.access_level = "RESTRICTED"
        user_info.save()
        self.assertEqual(get_request().status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(post_request().status_code, status.HTTP_403_FORBIDDEN)

        # Adding the facility to the access control should now allow the request to pass
        # Through
        facility = Facility.objects.get(facility_name="CoreFacilityName")
        FacilityAccessControl.objects.create(
            user=user, facility=facility
        )

        self.assertEqual(get_request().status_code, status.HTTP_200_OK)
        self.assertEqual(post_request().status_code, status.HTTP_200_OK)

        # Test that it fails if parameters are missing
        self.assertEqual(
            get_request(data={"division_name": "CoreDivisionName"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            post_request(data={"facility_name": "CoreFacilityName"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )

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

    def test_user_permission(self):
        # Testing pre-authorized user
        url = reverse("get_user_permission")
        response = self.client.get(url, data={"email": "TestUserEmail@gmail.com"})
        # Test that the user is not confirmed and it is not assigned to a customer
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["confirmed_user"], False)
        self.assertEqual(response.json()["customer"], None)

        # Creating a pre-authorized user should allow the user to be confirmed and assigned to a customer
        # But also we need a fast solution to only accept certain users to access Staples CA custom dashboard
        customer = Customer.objects.get(customer_name="CoreCustomerName")
        PreAuthorizedUser.objects.create(
            email="TestUserEmail@gmail.com",
            customer=customer,
            user_name="TestUserName",
            cs_staples_ca_ds=True,
        )
        url = reverse("get_user_permission")
        response = self.client.get(url, data={"email": "TestUserEmail@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["confirmed_user"], True)
        self.assertEqual(response.json()["customer"], "CoreCustomerName")
        self.assertEqual(response.json()["user_name"], "TestUserName")
        self.assertEqual(response.json()["cs_staples_ca_ds"], True)
        user = User.objects.get(username="CoreTestUser")
        self.assertEqual(user.email, "TestUserEmail@gmail.com")

    def test_bulk_create_facility(self):
        mock = [
            [
                "facility_name",
                "facility_identifier",
                "postal_code",
                "latitude",
                "longitude",
                "area",
                "address",
                "category_type",
                "closed",
            ],
            [
                "CoreFacilityName",
                "CoreFacilityIdentifier",
                "CFC",
                "10",
                "10",
                "0",
                "CoreAddress",
                "Retail",
                "False",
            ],
        ]
        bulk_create_facility(mock)
        facility = Facility.objects.get(facility_name="CoreFacilityName")
        self.assertEqual(facility.facility_name, "CoreFacilityName")
        self.assertEqual(facility.facility_identifier, "CoreFacilityIdentifier")
        self.assertEqual(facility.postal_code, "CFC")
        self.assertEqual(facility.latitude, 10)
        self.assertEqual(facility.longitude, 10)
        self.assertEqual(facility.area, 0)
        self.assertEqual(facility.address, "CoreAddress")
        self.assertEqual(facility.category_type, "Retail")
        self.assertEqual(facility.closed, False)
