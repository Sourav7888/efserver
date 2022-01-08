from celery import shared_task
from .etl import bulk_create_waste_data
from typing import Any
from apps.reports.models import Log


@shared_task
def async_bulk_create_waste_data(data: list[Any]) -> None:
    bulk = bulk_create_waste_data(data)
    Log.objects.create(log_name="bulk_create_waste_data", log_description=str(bulk))
