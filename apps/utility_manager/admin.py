from django.contrib import admin
from .models import UtilityBill


# Register your models here.
# An admin page for inline view of Facility and Utility Bill
class FacilityUtilityBillInline(admin.TabularInline):
    model = UtilityBill
    can_delete = False


admin.site.register(UtilityBill)
