from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncYear

# @NOTES Currently not used but tested
class WasteMonthlyManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .values("pickup_date__year", "pickup_date__month")
            .annotate(
                weight=Sum("weight"),
            )
            .order_by("pickup_date__year")
        )


class WasteYearlyManager(models.Manager):
    """
    Manager for yearly data, returns the yearly usage
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(year=TruncYear("pickup_date"))
            .values("year", "is_recycled")
            .annotate(
                weight=Sum("weight"),
            )
            .order_by("year")
        )
