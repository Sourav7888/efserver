from core.models import UserInfo
from apps.investigations.models import InvestigationAuthorization
from rest_framework.permissions import BasePermission
from typing import Union
from core.serializers import model_to_dict


def get_or_create_investigation_authorization(
    id: str, as_dict=False
) -> Union[bool, InvestigationAuthorization]:
    """
    Create investigation authorization if does not yet exist
    """

    user_info = UserInfo.objects.get(user_unique_id=id)
    inv_auth = InvestigationAuthorization.objects.filter(user_info=user_info)

    context = {}
    model = None

    if inv_auth.exists():
        context["status"] = True
        model = inv_auth.first()
    else:
        context["status"] = False
        model = InvestigationAuthorization.objects.create(user_info=user_info)

    if as_dict:
        context["model"] = model_to_dict(model)
    else:
        context["model"] = model

    return context


class HasInvestigationAccess(BasePermission):
    """
    Check that user have access to investigation
    """

    def has_permission(self, request, view):
        x = get_or_create_investigation_authorization(
            request.user.user_info.user_unique_id
        )

        if x["status"]:
            if x["model"].access_investigation:
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

        if x["status"]:
            if x["model"].is_investigation_manager:
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

        if x["status"]:
            if x["model"].is_investigator:
                return True

        return False
