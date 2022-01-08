from django.contrib import admin

from .models import *

admin.site.register(WasteData)
admin.site.register(WasteProvider)
admin.site.register(WasteCategory)
