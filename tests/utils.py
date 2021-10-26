from rest_framework.test import APITestCase
from core.models import Division, Facility, FacilityAccessControl, Customer, UserInfo
from django.contrib.auth.models import User


class BaseTest(APITestCase):
    # << ONLY USE self.data to access in setup ! Elsewhere must be hard coded >>
    data = {
        "user": {"username": "CoreTestUser", "password": "123"},
        "division": [
            {"division_name": "CoreDivisionName"},
            {"division_name": "CoreDivisionName2"},
        ],
        "facility": {"facility_name": "CoreFacilityName"},
        "customer": {"customer_name": "CoreCustomerName"},
    }

    def setUp(self):
        customer = Customer.objects.create(**self.data["customer"])

        # User by default acces_level="RESTRICTED" and customer will be null
        user = User.objects.create_user(**self.data["user"])

        # Division is associated with a customer
        division = Division.objects.create(
            **self.data["division"][0], customer=customer
        )
        facility = Facility.objects.create(**self.data["facility"], division=division)

        # Division not associated with a customer
        division2 = Division.objects.create(**self.data["division"][1])

        self.client.login(**self.data["user"])
