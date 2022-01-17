from django.db import models
from django.db.models import Sum


class RenewablesYearlyManager(models.Manager):
    """
    Manager for yearly data, returns the yearly usage
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .values(
                "year",
            )
            .annotate(
                purchased_energy=Sum("purchased_energy"),
                emission_reduction=Sum("emission_reduction"),
            )
            .order_by("year")
        )
