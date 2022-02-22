from django.db import models
from apps.etl.waste_manager.managers import WasteYearlyManager
from core.models import Facility
from .managers import WasteYearlyManager, WasteMonthlyManager


class WasteCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Waste Categories"


class WasteProvider(models.Model):
    provider_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.provider_name


class WasteData(models.Model):
    """
    pickup_date > Ususally a date within a given month is associated to that month typically the 1st day
    fk to facility > Enforced
    waste_name
    weight > in metric tons
    isRecycled
    waste_category > enforced so that filtering is always accurate
    provided_by
    """

    pickup_date = models.DateField(null=False, blank=False)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        db_column="facility",
        null=True,
        blank=True,
        to_field="facility_name",
    )
    waste_name = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=15, decimal_places=6, default=0.0)
    is_recycled = models.BooleanField(default=False, null=False, blank=False)
    waste_category = models.ForeignKey(
        WasteCategory,
        on_delete=models.CASCADE,
        db_column="waste_category",
        blank=False,
        null=False,
        to_field="category_name",
    )
    provided_by = models.ForeignKey(
        WasteProvider,
        on_delete=models.CASCADE,
        db_column="provided_by",
        to_field="provider_name",
    )

    objects = models.Manager()

    yearly = WasteYearlyManager()

    monthly = WasteMonthlyManager()

    class Meta:
        verbose_name_plural = "Waste Data"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "facility",
                    "pickup_date",
                    "waste_name",
                    "waste_category",
                    "is_recycled",
                ],
                name="no_duplicate_waste_data",
            )
        ]

    def __str__(self):
        return (
            f"{self.facility} - {self.pickup_date} - {self.waste_name} - {self.weight}"
        )
