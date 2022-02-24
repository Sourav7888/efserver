from core.models import Facility
from core.tests.utils import BaseTest
from apps.high_consumptions.tasks import (
    create_hc_investigation,
    create_hc_report,
    generate_hc,
    generate_hc_by_division,
)
from apps.investigations.models import Investigation
from apps.high_consumptions.models import HC, HCReportTracker
from apps.reports.models import Report
import uuid


class BaseTestCase(BaseTest):
    def test_create_hc_report(self):
        facility = Facility.objects.get(facility_name="CoreFacilityName")
        report_id = create_hc_report(facility, None, "", include_document=False)

        self.assertEqual(True, Report.objects.filter(report_id=report_id).exists())

    def test_create_hc_investigation(self):
        facility = Facility.objects.get(facility_name="CoreFacilityName")
        hc_id = create_hc_investigation(
            facility, None, "HC_WT", "2020-01-01", "", include_document=False
        )

        self.assertEqual(
            True, Investigation.objects.filter(investigation_id=hc_id).exists()
        )

    # @NOTE: Just making sure that this runs without failing
    def test_generate_hc(self):
        _id = uuid.uuid4()
        generate_hc("electricity", "2020-01-01", _id)
        self.assertEqual(False, HC.objects.filter(hc_id=_id).exists())

    def test_generate_hc_by_division(self):
        """
        Tested in views
        """
        _id = HCReportTracker.objects.create(hc_report_id=uuid.uuid4())
        generate_hc_by_division.delay(
            _id.hc_report_id,
            "CoreDivisionName",
            "electricity",
            "2020-01-01",
        )
        self.assertEqual(
            True, HCReportTracker.objects.get(hc_report_id=_id.hc_report_id).is_ready
        )
