from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncYear


class WasteYearlyManager(models.Manager):
    """
    Manager for yearly data, returns the yearly usage
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(year=TruncYear("pickup_date"))
            .values("year")
            .annotate(
                weight=Sum("weight"),
            )
            .order_by("year")
        )
