from apps.utility_manager.models import UtilityBill
from core.models import Facility
from core.tests.utils import BaseTest


class ManagersTestCase(BaseTest):
    def setUp(self):
        super().setUp()
        facility = Facility.objects.get(
            facility_name=self.data["facility"]["facility_name"]
        )
        UtilityBill.objects.create(
            facility=facility,
            billing_date="2021-10-10",
            utility_type="Electricity",
            usage=100,
        )
        UtilityBill.objects.create(
            facility=facility,
            billing_date="2021-10-9",
            utility_type="Electricity",
            usage=100,
        )
        UtilityBill.objects.create(
            facility=facility,
            billing_date="2021-8-10",
            utility_type="Electricity",
            usage=100,
        )

    def test_yearly_manager(self):
        # Create a few utility objects
        facility = Facility.objects.get(
            facility_name=self.data["facility"]["facility_name"]
        )
        yearly = int(UtilityBill.yearly.all().first()["usage"])
        self.assertEqual(yearly, 300)

    def test_monthly_manager(self):
        # Create a few utility objects
        facility = Facility.objects.get(
            facility_name=self.data["facility"]["facility_name"]
        )
        monthly = UtilityBill.monthly.filter()
        self.assertEqual(int(monthly[1]["usage"]), 200)
