from enum import unique
from django.db import models
from apps.high_consumptions.storages_backends import HCDocs
from core.models import Facility, UserInfo
import uuid

# Create your models here.
class HC(models.Model):
    hc_id = models.UUIDField(default=uuid.uuid4, null=False, blank=False)

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        to_field="facility_name",
        db_column="facility",
    )

    usage_increase = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, null=False, blank=False
    )

    cost_increase = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, null=False, blank=False
    )

    target_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    utility_type = models.CharField(max_length=25, null=True, blank=True)

    hc_document = models.FileField(storage=HCDocs(), null=True, blank=True)

    def __str__(self):
        return f"{self.facility} - {self.target_date} - {self.created_at}"


class HCReportTracker(models.Model):
    """
    Tracks the state of the reports as well as
    who created them
    """

    hc_report_id = models.CharField(
        max_length=255, null=False, blank=False, unique=True
    )

    creator = models.ForeignKey(
        UserInfo,
        on_delete=models.DO_NOTHING,
        db_column="creator",
        null=True,
        blank=True,
        to_field="user_unique_id",
        related_name="hc_report_tracker_creator",
    )

    report_metadata = models.JSONField(null=True, blank=True)
    is_ready = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.creator} - {self.created_at} - {self.is_ready} - {self.hc_report_id}"
