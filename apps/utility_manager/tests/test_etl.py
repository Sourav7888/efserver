from core.tests.utils import BaseTest
from apps.utility_manager.models import UtilityBill
from apps.utility_manager.etl import bulk_create_utility
from core.models import Facility


class ETLTestCase(BaseTest):
    def test_etl(self):
        # (facility, billing_date, utility_type, cost, usage, unit, billing_days)
        data = [  # normal data
            ["CoreFacilityName", "2023-01-01", "Electricity", "10", "10", "kwh", 1],
        ]
        # Test Create
        bulk_create_utility(data)

        facility = Facility.objects.get(facility_name="CoreFacilityName")

        utility = UtilityBill.objects.get(
            facility=facility, billing_date="2023-01-01", utility_type="Electricity"
        )

        self.assertEqual(int(utility.cost), 10)
        self.assertEqual(int(utility.usage), 10)

        update = [  # normal data
            ["CoreFacilityName", "2023-01-01", "Electricity", "15", "15", "kwh", 10],
        ]

        # Test Update

        bulk_create_utility(update)
        utility = UtilityBill.objects.get(
            facility=facility, billing_date="2023-01-01", utility_type="Electricity"
        )
        self.assertEqual(int(utility.cost), 15)
        self.assertEqual(int(utility.usage), 15)
        self.assertEqual(int(utility.billing_days), 10)

