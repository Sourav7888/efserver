from core.models import Facility
from apps.investigations.models import Investigation
from io import BytesIO
from django.core.files.base import ContentFile
from .base import GasHighConsumption, ElectricityHighConsumption
from .cs_exeptions import TargetDateNotFound, EmptyDataFrame
from django.db.utils import IntegrityError
from celery import shared_task
from apps.investigations.tasks import send_created_investigation
from .base import HighConsumption


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


# @TODO: Add a logger -- Some dashboard of sorts


# @TODO: Test
def generate_hc(
    hc_method: HighConsumption,
    target_date: str,
    hc_type: str,
    counter_limit: int = 3,
    warn: bool = True,
    **kwargs,
):
    """
    HC_METHOD: The high consumption object
    target_date: The date to be used as the target date
    hc_type: The type of high consumption
    counter_limit: The number of times the target date has to be found
    **kargs is the render arguments
    """
    facilities = Facility.objects.all()

    counter = 0

    for f in facilities:
        hc = hc_method.create_hc_by_facility_obj(f, target_date)
        try:
            hc.run_method()
        except (TargetDateNotFound, EmptyDataFrame):
            continue

        # if high consuming
        if hc.is_hc():
            template = hc.render_template(**kwargs)
            try:
                # @TODO Doing this is very expensive, refractor next time
                # Test that the investigation does not already exist
                create_hc_investigation(
                    f, template, hc_type, target_date, hc.get_description()
                )

                info = {
                    "facility": f.facility_name,
                    "investigation_date": target_date,
                    "investigation_type": hc_type,
                    "investigation_description": hc.get_description(),
                }

                counter += 1

                print(info)

                if warn:
                    send_created_investigation(info)

            except IntegrityError:
                continue

        if counter == counter_limit:
            # End the task when the counter limit is reached
            break


@shared_task
def generate_gas_high_consumption(target_date: str, counter_limit: int = 3):
    """
    Generate gas high_consumption based on simple linear regression and cost increase
    """
    generate_hc(
        GasHighConsumption,
        target_date,
        "HC_GAS",
        warn=True,
        counter_limit=counter_limit,
        facility_context=True,
        stats_context=True,
    )


@shared_task
def generate_electricity_high_consumtion(target_date, counter_limit: int = 3):
    """
    Generate electricity high consumption
    """
    generate_hc(
        ElectricityHighConsumption,
        target_date,
        "HC_EL",
        warn=True,
        counter_limit=counter_limit,
        facility_context=True,
    )
