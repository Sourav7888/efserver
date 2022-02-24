from core.models import Facility
from apps.investigations.models import Investigation
from io import BytesIO
from django.core.files.base import ContentFile
from .cs_exeptions import TargetDateNotFound, EmptyDataFrame
from celery import shared_task, uuid
from .base import ElectricityHighConsumption, GasHighConsumption, HighConsumption
from apps.reports.models import Log, Report
from .models import HC, HCReportTracker
from apps.shared.utils import upload_model_document
import uuid

HC_METHODS = {
    "electricity": ElectricityHighConsumption,
    "natural gas": GasHighConsumption,
}

HC_CODES = {
    "electricity": "HC_EL",
    "natural gas": "HC_NG",
}


def create_hc_report(
    facility: Facility,
    template: bytes,
    report_desc: str,
    include_document: bool = True,
):
    report = Report.objects.create(
        report_name=f"HC-Report -- {facility.facility_name}",
        report_description=report_desc,
    )

    if include_document:
        upload_report_document(report, template)

    return report.report_id


# @NOTE: Will be deprecated in favor of a generic one
def upload_report_document(report: Report, template: bytes):
    """
    Upload the document to the report model
    """
    buffer = BytesIO()
    buffer.write(template)
    content = ContentFile(buffer.getvalue())
    report.report_file.save(f"{report.report_id}.html", content)
    report.save()


def create_hc_investigation(
    facility: Facility,
    template: bytes,
    investigation_type: str,
    investigation_date: str,
    investigation_description: str,
    include_document: bool = True,
    **kwargs,
):
    """
    Creates a high consumption investigation
    """
    investigation = Investigation.objects.create(
        facility=facility,
        investigation_type=investigation_type,
        investigation_date=investigation_date,
        investigation_description=investigation_description,
        **kwargs,
    )

    if include_document:
        upload_hc_document(investigation, template)

    return investigation.investigation_id


# @NOTE: Will be deprecated in favor of a generic one
def upload_hc_document(investigation: Investigation, template: bytes):
    """
    Upload the document to the investigation
    """
    buffer = BytesIO()
    buffer.write(template)
    content = ContentFile(buffer.getvalue())
    investigation.investigation_document.save(
        f"{investigation.investigation_id}.html", content
    )
    investigation.save()


@shared_task
def generate_hc(utility_type: str, target_date: str, hc_id: uuid):
    """
    HC_METHOD: The high consumption object
    target_date: The date to be used as the target date
    hc_id: report id
    """

    facilities = Facility.objects.all()

    for f in facilities:
        hc = HC_METHODS[utility_type].create_hc_by_facility_obj(f, target_date)
        try:
            hc.run_method()
        except (TargetDateNotFound, EmptyDataFrame):
            continue

        if hc.is_hc():
            HC.objects.create(
                facility=f,
                target_date=target_date,
                usage_increase=round(hc.context["percentage_diff"], 2),
                cost_increase=round(hc.context["estimated_cost"], 2),
                hc_id=hc_id,
                utility_type=utility_type,
            )


# @TODO: Test if needed - Non-critical
def generate_hc_report_by_facility(
    facility: Facility,
    hc_method: HighConsumption,
    target_date: str,
    **kwargs,
):
    hc = hc_method.create_hc_by_facility_obj(facility, target_date)

    log_description = ""

    report = None

    try:
        hc.run_method()
        log_description = "Successfully generated HC report"
        # There is no point in rendering the template if there is non data
        report = create_hc_report(
            facility, hc.render_template(**kwargs), log_description
        )
    except (TargetDateNotFound, EmptyDataFrame) as e:
        log_description = str(e)

    # Create a log
    Log.objects.create(
        log_name=f"HC Report -- Facility: {facility.facility_name}",
        log_description=log_description,
    )

    return report


@shared_task
def generate_hc_by_division(
    _id: str,
    division: str,
    utility_type: str,
    investigation_date: str,
    include_document: bool = False,
):
    facilities = Facility.objects.filter(division=division).select_related("division")

    for f in facilities:
        hc = HC_METHODS[utility_type].create_hc_by_facility_obj(f, investigation_date)
        try:
            hc.run_method()
        except (TargetDateNotFound, EmptyDataFrame):
            continue

        if hc.is_hc():
            hc_obj = HC.objects.create(
                facility=f,
                target_date=investigation_date,
                usage_increase=round(hc.context["percentage_diff"], 2),
                cost_increase=round(hc.context["estimated_cost"], 2),
                hc_id=_id,
                utility_type=HC_CODES[utility_type],
            )

            if include_document:
                upload_model_document(
                    hc_obj,
                    "hc_document",
                    f"{str(uuid.uuid4())}.html",
                    hc.render_template(facility_context=True, stats_context=True),
                )

    hc_tracker = HCReportTracker.objects.get(hc_report_id=_id)
    hc_tracker.is_ready = True
    hc_tracker.save()
