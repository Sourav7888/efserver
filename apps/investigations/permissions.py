from core.models import UserInfo
from apps.investigations.models import InvestigationAuthorization
from rest_framework.permissions import BasePermission
from typing import Union


def get_or_create_investigation_authorization(
    id: str,
) -> Union[bool, InvestigationAuthorization]:
    """
    Create investigation authorization if does not yet exist
    """

    user_info = UserInfo.objects.get(user_unique_id=id)
    inv_auth = InvestigationAuthorization.objects.filter(user_info=user_info)
    if inv_auth.exists():
        return inv_auth.first()

    else:
        InvestigationAuthorization.objects.create(user_info=user_info)
        return False


class HasInvestigationAccess(BasePermission):
    """
    Check that user have access to investigation
    """

    def has_permission(self, request, view):
        x = get_or_create_investigation_authorization(
            request.user.user_info.user_unique_id
        )

        if x:
            if x.access_investigation:
                return True

        return False


class IsInvestigationManager(BasePermission):
    """
    Check that the user is an investigator
    """

    def has_permission(self, request, view):

        x = get_or_create_investigation_authorization(
            request.user.user_info.user_unique_id
        )

        if x:
            if x.is_investigation_manager:
                return True

        return False


class IsInvestigator(BasePermission):
    """
    Check if a user is an investigator
    """

    def has_permission(self, request, view):
        x = get_or_create_investigation_authorization(
            request.user.user_info.user_unique_id
        )

        if x:
            if x.is_investigator:
                return True

        return False
