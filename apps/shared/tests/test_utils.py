import uuid
from rest_framework.test import APITestCase
from apps.reports.models import Report
from ..utils import upload_model_document


class UtilsTestCase(APITestCase):
    def test_upload_model_document(self):
        report = Report.objects.create()

        self.assertEqual(None, report.report_file.name)

        doc = b"""
        <html>
            <head>
                <title>Test</title>
            </head>
        </html>
        """

        file_name = str(uuid.uuid4())

        upload_model_document(report, "report_file", file_name, doc)

        self.assertEqual(file_name, report.report_file.name)
