from .models import Division, Facility, FacilityAccessControl
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User


class CheckRequestBody(BasePermission):
    """
    This permission check the request body keyword
    This only check a single instance ie: Division: exampleDivision and not Division: [Division1, ...]
    This catches wether the queried instance exist or not as well so that will be handled by a 403
    When using this permission the request body to check division and facility must be
    facility_name and division_name
    """

    def has_permission(self, request, view):
        types = ["POST", "HEAD", "DELETE", "GET", "PUT", "PATCH"]
        data = [getattr(request, x) for x in types if getattr(request, x, None)]

        # Check the request body
        if data:
            if "division_name" in data[0]:
                try:
                    _division = Division.objects.get(division_name=data[0]["division_name"])
                except Division.DoesNotExist:
                    return False

                if request.user.user_info.customer != _division.customer:
                    return False

            if "facility_name" in data[0]:
                try:
                    facility = Facility.objects.get(
                        facility_name=data[0]["facility_name"]
                    )

                    # Check if the facility is of the same customer base
                    if request.user.user_info.customer != facility.division.customer:
                        return False

                    # Otherwise check this user
                    # Check the user access
                    if request.user.user_info.access_level == "RESTRICTED":
                        access_control = FacilityAccessControl.objects.filter(
                            user=request.user, facility=facility
                        )
                        if not access_control.exists():
                            return False

                except (Facility.DoesNotExist, FacilityAccessControl.DoesNotExist):
                    return False

        return True
