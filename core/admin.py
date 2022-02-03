from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from apps.utility_manager.admin import FacilityUtilityBillInline
from apps.etl.waste_manager.admin import FacilityWasteDataInline
from apps.investigations.admin import InvestigationAuthorizationInline


# ------------------ Add users related inlines here ------------------ #
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


# ------------------ Add apps authorizations inlines here ------------------ #
class UserInfoAdmin(admin.ModelAdmin):
    inlines = (InvestigationAuthorizationInline,)


# ------------------ Add apps facilities inlines here ------------------ #


class FacilityAdmin(admin.ModelAdmin):
    inlines = [FacilityUtilityBillInline, FacilityWasteDataInline]


# User
admin.site.register(Customer)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# User Info
admin.site.register(UserInfo, UserInfoAdmin)

# Division
admin.site.register(Division)

# Facility
admin.site.register(Facility, FacilityAdmin)

# PreAuthorizedUser
admin.site.register(PreAuthorizedUser)
