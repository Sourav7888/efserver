from django.db import models
from core.models import UserInfo, Facility
from uuid import uuid4
from .storages_backends import InvestigationDocs
from core.models import UserInfo


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
        to_field="user_unique_id",
        related_name="investigation_investigator",
    )
    investigation_creator = models.ForeignKey(
        UserInfo,
        on_delete=models.DO_NOTHING,
        db_column="investigation_creator",
        null=True,
        blank=True,
        to_field="user_unique_id",
        related_name="investigation_creator",
    )
    investigation_tech = models.ForeignKey(
        UserInfo,
        on_delete=models.DO_NOTHING,
        db_column="investigation_tech",
        null=True,
        blank=True,
        to_field="user_unique_id",
        related_name="investigation_tech",
    )
    investigation_date = models.DateField(null=False, blank=False)
    investigation_type = models.CharField(
        max_length=6, choices=HIGH_CONSUMPTION_OPTIONS
    )
    investigation_description = models.TextField(null=True, blank=True)
    investigation_document = models.FileField(
        storage=InvestigationDocs(), null=True, blank=True
    )
    investigation_result = models.TextField(null=True, blank=True)
    investigation_bas_fix = models.TextField(null=True, blank=True)
    require_bas_fix = models.BooleanField(default=False, null=False, blank=False)
    in_approval = models.BooleanField(default=False, null=False, blank=False)
    closed = models.BooleanField(default=False, null=False, blank=False)

    investigation_metadata = models.JSONField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "investigation_type", "investigation_date"],
                name="no_duplicate_investigations",
            )
        ]

    def __str__(self):
        val = f"""
        Facility: {self.facility} 
        | Type: {self.investigation_type} 
        | Date: {self.investigation_date} 
        | In Approval: {self.in_approval} 
        | Closed: {self.closed} 
        """

        try:
            val += f" | Investigator: {self.investigation_investigator.user_name} | Investigator: {self.investigation_tech.user_name}"
        except (AttributeError, UserInfo.DoesNotExist):
            pass

        return val


class InvestigationAuthorization(models.Model):
    user_info = models.OneToOneField(
        UserInfo,
        on_delete=models.SET_NULL,
        db_column="user_info",
        null=True,
        to_field="user_unique_id",
        related_name="investigation_authorization",
        unique=True,
    )

    # @TODO: These need to be moved to an investigation permissions model
    # Access to investigations
    access_investigation = models.BooleanField(default=False, null=False, blank=False)

    # Allow to address investigations -> Can grab Investigations and investigate
    # And submit for approval to the manager
    is_investigator = models.BooleanField(default=False, null=False, blank=False)

    # Allow to approve and create investigations -> Can Create|Delete|Approve Investigations
    is_investigation_manager = models.BooleanField(
        default=False,
        blank=False,
    )

    def __str__(self):
        return f"Name: {self.user_info}"
