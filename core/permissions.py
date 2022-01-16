from .models import Division, Facility, FacilityAccessControl, UserInfo
from rest_framework.permissions import BasePermission
from django.http import HttpRequest


def get_or_create_user_info(request: HttpRequest) -> UserInfo:
    """
    Check if this user has user info yet, if not create one
    When using remote user with auth 0 will only
    Create the user with a username (unique) in the database
    """

    user_info = UserInfo.objects.filter(user=request.user)

    if not user_info.exists():
        return UserInfo.objects.create(user=request.user)

    return user_info.first()


def validate_facility_access(request: HttpRequest) -> Facility:
    """
    Will validate the request and always only return what facility the user is allowed to access
    """
    # Check that the user has UserInfo already created if not create
    if not hasattr(request.user, "user_info"):
        get_or_create_user_info(request)

    user_info = request.user.user_info
    customer = user_info.customer
    access_level = user_info.access_level
    facilities = Facility.objects.filter(division__customer=customer).select_related(
        "division"
    )

    # Make an exeption for enerfrog staff access level
    if access_level == "ENERFROG_STAFF":
        return facilities

    if access_level == "RESTRICTED":
        access_control = (
            FacilityAccessControl.objects.filter(user=request.user)
            .select_related("user")
            .select_related("facility")
        )

        if access_control.exists():
            try:
                allowed_access = [x.facility.facility_name for x in access_control]
                return Facility.objects.filter(
                    facility_name__in=allowed_access
                ).select_related("division")
            except TypeError:
                pass

        return Facility.objects.none()

    else:
        return Facility.objects.filter(division__customer=customer).select_related(
            "division"
        )


class CheckRequestBody(BasePermission):
    """
    @WARNING: This only works if the models has a foreign key relationship with
    core division or facility

    @Warning: Make sure that the variables division or facility are required in the api
    otherwise users can ommit those and access the data

    This permission check the request body
    This only check a single instance ie: Division: exampleDivision and not Division: [Division1, ...]
    This catches whether the queried instance exist or not as well so that will be handled by a 403
    When using this permission the request body to check division and facility must be
    facility_name and division_name

    If user_info has not been created as well this will handle it
    """

    def has_permission(self, request, view):
        body = getattr(request, request.method, None)
        # Check that the user has UserInfo already created if not create
        if not hasattr(request.user, "user_info"):
            get_or_create_user_info(request)

        # Check the request body
        if body:
            if not self.has_division_permission(request, body):
                return False

            if not self.has_facility_permission(request, body):
                return False

        return True

    def has_division_permission(self, request, body) -> bool:
        """
        Check division permission if in body
        """
        if "division_name" in body or "division" in body:
            try:
                var = "division_name" if "division_name" in body else "division"
                _division = Division.objects.get(division_name=body[var])
            except Division.DoesNotExist:
                return False

            if request.user.user_info.customer != _division.customer:
                return False

        return True

    def has_facility_permission(self, request, body) -> bool:
        """
        Check facility permission if in body
        """
        if "facility_name" in body or "facility" in body:
            var = "facility_name" if "facility_name" in body else "facility"
            try:
                facility = Facility.objects.get(facility_name=body[var])

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
