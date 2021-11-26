from django.contrib import admin
from .models import *


class ShowRO(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


# Register your models here.
admin.site.register(Log, ShowRO)
admin.site.register(Report, ShowRO)
