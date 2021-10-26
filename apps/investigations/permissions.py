from core.models import UserInfo
from rest_framework.permissions import BasePermission


class HasInvestigationAccess(BasePermission):
    """
    Check that user have access to investigation
    """

    def has_permission(self, request, view):

        if request.user.user_info.access_investigation:

            return True

        return False


class IsInvestigationManager(BasePermission):
    """
    Check that the user is an investigator
    """

    def has_permission(self, request, view):

        if request.user.user_info.is_investigation_manager:

            return True

        return False


class IsInvestigator(BasePermission):
    """
    Check if a user is an investigator
    """

    def has_permission(self, request, view):
        if request.user.user_info.is_investigator:

            return True

        return False
