from celery import shared_task
from .etl import bulk_create_facility
from typing import Any
from apps.reports.models import Log


@shared_task
def async_bulk_create_facility(data: list[Any]) -> None:
    bulk = bulk_create_facility(data)
    Log.objects.create(log_name="bulk_create_facility", log_description=str(bulk))
