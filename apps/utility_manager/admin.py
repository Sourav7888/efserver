from django.contrib import admin
from core.models import Facility
from .models import UtilityBill


# Register your models here.
# An admin page for inline view of Facility and Utility Bill
class FacilityUtilityBillInline(admin.TabularInline):
    model = UtilityBill
    can_delete = False


admin.site.register(UtilityBill)
