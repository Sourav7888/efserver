from django.contrib import admin
from .models import Investigation, InvestigationAuthorization

# Add the user info inline in django admin
class InvestigationAuthorizationInline(admin.StackedInline):
    model = InvestigationAuthorization
    can_delete = False


admin.site.register(Investigation)
