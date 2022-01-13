from django.contrib import admin

from .models import *


# Register your models here.
# An admin page for inline view of Facility and Utility Bill
class FacilityWasteDataInline(admin.TabularInline):
    model = WasteData
    can_delete = False


admin.site.register(WasteProvider)
admin.site.register(WasteCategory)
