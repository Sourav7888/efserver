from django.db import models
from core.models import UserInfo, Facility
from uuid import uuid4

HIGH_CONSUMPTION_OPTIONS = [
    ("HC_WT", "HC_WT"),
    ("HC_GAS", "HC_GAS"),
    ("HC_EL", "HC_EL"),
]

# Create your models here.
class Investigation(models.Model):
    investigation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        db_column="facility",
        null=True,
        blank=True,
        to_field="facility_name",
    )
    investigation_investigator = models.ForeignKey(
        UserInfo,
        on_delete=models.DO_NOTHING,
        db_column="investigation_investigator",
        null=True,
        blank=True,
        to_field="user_id",
        related_name="investigation_investigator",
    )
    investigation_creator = models.ForeignKey(
        UserInfo,
        on_delete=models.DO_NOTHING,
        db_column="investigation_creator",
        null=True,
        blank=True,
        to_field="user_id",
        related_name="investigation_creator",
    )
    investigation_date = models.DateField(null=False, blank=False)
    investigation_type = models.CharField(
        max_length=6, choices=HIGH_CONSUMPTION_OPTIONS
    )
    investigation_description = models.TextField(null=True, blank=True)
    investigation_result = models.TextField(null=True, blank=True)

    in_approval = models.BooleanField(default=False, null=False, blank=False)
    closed = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "investigation_type", "investigation_date"],
                name="no_duplicate_investigations",
            )
        ]

    def __str__(self):
        return f"Investigation for: {self.facility} | Type: {self.investigation_type} | {self.investigation_date}"
