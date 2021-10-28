from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


# Add the user info inline in django admin
class UserInfoInline(admin.StackedInline):
    model = UserInfo
    can_delete = False


# Add the user info inline in django admin
class FacilitAccessControlInline(admin.TabularInline):
    model = FacilityAccessControl
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (
        UserInfoInline,
        FacilitAccessControlInline,
    )


admin.site.register(Customer)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Division)
admin.site.register(Facility)
admin.site.register(FacilityAccessControl)
admin.site.register(UserInfo)
