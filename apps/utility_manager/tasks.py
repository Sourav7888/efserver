from celery import shared_task
from .etl import bulk_create_utility
from typing import Any
from django.core.mail import send_mail

# @TODO: Add some sort of a logger
# @TODO: This is a quick fix for the notification
@shared_task
def async_bulk_create_utility(data: list[Any]) -> None:
    bulk = bulk_create_utility(data)
    send_mail(
        "Bulk-Create-Utility-Result",
        str(bulk),
        "tantely.raza@enerfrog.com",
        ["tantely.raza@enerfrog.com"],
    )
