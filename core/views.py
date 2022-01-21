from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cs_schema import TestViewSc, UserInfo
from django.utils.decorators import method_decorator
from core.permissions import CheckRequestBody, validate_facility_access
from rest_framework.permissions import IsAuthenticated
from .permissions import get_or_create_user_info
from rest_framework.generics import RetrieveAPIView, ListAPIView
from .serializers import UserInfoSr, DivisionSr
from .paginations import DivisionPg
from .models import Division
from .serializers import FacilitySr
from .paginations import FacilityPg
from .models import PreAuthorizedUser
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User


@method_decorator(
    **TestViewSc,
)
class CoreTestView(APIView):
    """
    Dummy to test permission class # Do Not Use!
    """

    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get(self, request):
        return Response({"message": "hello world"}, status=status.HTTP_200_OK)


@method_decorator(**UserInfo)
class UserPermission(RetrieveAPIView):
    """
    Return the user permissions across modules
    """

    serializer_class = UserInfoSr

    def get_object(self):
        # Create the user info if it does not exist yet
        # Because usually this view is called as soon as the user log in
        user_info = get_or_create_user_info(self.request)

        # Check if user is not confirmed
        # Check preauthorized users and if exists update informations and that 's it <This is for sustainability dashboard>
        # To streamline users coming in to the dashboard
        if not user_info.confirmed_user:
            email = self.request.query_params.get("email")
            if email:
                user_check = PreAuthorizedUser.objects.filter(email=email)
                if user_check.exists():
                    user_info.confirmed_user = True
                    user_info.user_name = user_check[0].user_name
                    user_info.customer = user_check[0].customer
                    user_info.is_investigator = False
                    # @NOTE: This need to be all as certain data are dependent on how many facilities
                    # The user has access to
                    # @TODO: Add an exception in the validate_facility_access that if the user has dashboard access
                    # Allow all or separate the permissions in both
                    user_info.access_level = "ALL"
                    user_info.save()

                    # Update the users' email
                    user = User.objects.get(id=user_info.user.id)
                    user.email = email
                    user.save()

                    return user_info

        return user_info


class DivisionList(ListAPIView):
    """
    Returns a list of all available divisions if not filtered by division_name
    """

    serializer_class = DivisionSr
    filterset_fields = ["division_name"]
    pagination_class = DivisionPg

    def get_queryset(self):
        customer = self.request.user.user_info.customer
        divisions = Division.objects.filter(customer=customer)

        return divisions


class FacilityList(ListAPIView):
    """
    Returns a list of all facilities
    If user access is set to RESTRICTED
    The view will check the access control straight away
    even if a not authorized site is attributed to that list it will never show up
    on the api response as it is filtered by customer base
    """

    serializer_class = FacilitySr
    filterset_fields = "__all__"
    pagination_class = FacilityPg

    def get_queryset(self):
        facilities = validate_facility_access(self.request)
        return facilities
