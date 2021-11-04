from django.db import models
from core.models import Facility
from .managers import MonthlyUtilityBillManager, YearlyUtilityBillManager

TYPE_CHOICES = [
    ("Electricity", "Electricity"),
    ("NaturalGas", "NaturalGas"),
    ("Water", "Water"),
]


class UtilityBill(models.Model):
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        to_field="facility_name",
        db_column="facility",
    )

    billing_date = models.DateField(null=False, blank=False)
    utility_type = models.CharField(
        max_length=15, choices=TYPE_CHOICES, null=False, blank=False
    )
    usage = models.DecimalField(
        max_digits=13, decimal_places=3, default=0, null=False, blank=False
    )
    unit = models.CharField(max_length=10, null=True, blank=True)
    billing_days = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=13, decimal_places=3, default=0, null=False, blank=False
    )

    # Default Manager
    objects = models.Manager()
    # For Yearly data
    yearly = YearlyUtilityBillManager()
    # For Monthly data
    monthly = MonthlyUtilityBillManager()

    class Meta:
        verbose_name_plural = "Utility Manager"
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "billing_date", "utility_type"],
                name="no_duplicate_utility_data",
            )
        ]

    def __str__(self):
        return f"Type: {self.utility_type} | {self.billing_date} | {self.facility}"
