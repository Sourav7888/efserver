from django.db import models
from core.models import Facility

DIVISION_CHOISES = (
    ("retail", "retail"),
    ("professional", "professional"),
)


class Renewables(models.Model):

    year = models.IntegerField(null=False, blank=False)
    purchased_energy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emission_reduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    division = models.CharField(
        choices=DIVISION_CHOISES, max_length=25, null=False, blank=False
    )
    buyer = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Renewable Energy"
        constraints = [
            models.UniqueConstraint(
                fields=["year", "purchased_energy", "division", "buyer"],
                name="no_duplicate_renewable_data",
            )
        ]

    def __str__(self):
        return f"{self.year} - {self.division} - {self.buyer}"


class LedList(models.Model):
    retrofit_date = models.DateField(null=False, blank=False)
    vendor = models.CharField(max_length=255, null=False, blank=False)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        to_field="facility_name",
        db_column="facility",
    )

    class Neta:
        constants = [
            models.UniqueConstraint(
                fields=["retrofit", "vendor", "facility"],
                name="no_duplicate_led_data",
            )
        ]
