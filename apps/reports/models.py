from django.db import models
import uuid
from .storages_backends import LogsDocs, ReportsDocs
from core.models import Customer, UserInfo

# Create your models here.
class Log(models.Model):
    """
    Logs model used for storing logs accross the system when needed
    """

    log_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    log_name = models.CharField(max_length=255, blank=False, null=False)
    log_description = models.TextField(blank=True, null=True)
    log_file = models.FileField(storage=LogsDocs(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.log_name} | log_id: {self.log_id} | {self.created_at}"


class Report(models.Model):
    """
    Report model used for any type of reports
    """

    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report_name = models.CharField(max_length=255, blank=False, null=False)
    report_description = models.TextField(blank=True, null=True)
    report_file = models.FileField(storage=ReportsDocs(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        UserInfo,
        on_delete=models.SET_NULL,
        db_column="user",
        null=True,
        to_field="user_unique_id",
        related_name="user_report",
    )
    is_ready = models.BooleanField(default=False, null=False)

    def __str__(self):
        return f"{self.report_name} | report_id: {self.report_id}"


class CustomerReport(models.Model):
    """
    Safe To Use for Customers
    """

    report_name = models.CharField(max_length=255, blank=False, null=False)
    report_description = models.TextField(blank=True, null=True)
    report_file = models.FileField(storage=ReportsDocs(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        db_column="customer",
        null=True,
        blank=True,
        to_field="customer_name",
    )

    def __str__(self):
        return f"{self.report_name} | {self.customer} | {self.created_at}"
