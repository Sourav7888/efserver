from django.db import models
from core.models import Facility
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
        max_digits=7, decimal_places=3, default=0, null=False, blank=False
    )

    cost_increase = models.DecimalField(
        max_digits=7, decimal_places=3, default=0, null=False, blank=False
    )

    target_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    utility_type = models.CharField(max_length=25, null=True, blank=True)
