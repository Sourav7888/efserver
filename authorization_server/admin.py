from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Role)
admin.site.register(Platform)
admin.site.register(Permission)
admin.site.register(User)
