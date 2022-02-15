from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from core.permissions import CheckRequestBody, validate_facility_access
from rest_framework.permissions import IsAuthenticated
from .permissions import get_or_create_user_info, enforce_parameters
from rest_framework.generics import ListAPIView
from .serializers import DivisionSr, model_to_dict
from .paginations import DivisionPg
from .models import Division
from .serializers import FacilitySr
from .paginations import FacilityPg
from .models import PreAuthorizedUser, UserInfo
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from apps.shared.parsers import parse_in_memory_csv
from .tasks import async_bulk_create_facility
from apps import investigations
from rest_framework.response import Response


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "facility_name",
                    in_=openapi.IN_QUERY,
                    description="facility_name",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "division_name",
                    in_=openapi.IN_QUERY,
                    description="division_name",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class CoreTestView(APIView):
    """
    Dummy to test permission class # Do Not Use!
    Mainly to check permission Check request body
    which has to check query params on get and body on post
    also the decorator enforce_parameters testing as drf_yasg
    does not actually enforce the parameters to be present
    """

    permission_classes = [IsAuthenticated, CheckRequestBody]

    @method_decorator(enforce_parameters(params=["facility_name", "division_name"]))
    def get(self, request):
        return Response({"message": "hello world"}, status=status.HTTP_200_OK)

    @method_decorator(enforce_parameters(params=["facility_name", "division_name"]))
    def post(self, request):
        return Response({"message": "hello world"}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "email",
                    in_=openapi.IN_QUERY,
                    description="user email",
                    type=openapi.TYPE_STRING,
                ),
            ]
        ),
    }
)
class UserPermission(APIView):
    """
    Return the user permissions across modules
    """

    def perform_pre_authorized_user_check(self, email: str, user_info: UserInfo):
        user_check = PreAuthorizedUser.objects.filter(email=email)
        if user_check.exists():
            user_info.confirmed_user = True
            user_info.user_name = user_check[0].user_name
            user_info.customer = user_check[0].customer
            # @NOTE: This need to be all as certain data are dependent on how many facilities
            # The user has access to
            # @NOTE: For subsequent apps create a different permission models that handle platforma accessing
            # @TODO: Add an exception in the validate_facility_access that if the user has dashboard access
            # Allow all or separate the permissions in both
            user_info.access_level = "ALL"
            user_info.cs_staples_ca_ds = user_check[0].cs_staples_ca_ds

            user_info.save()

            # Update the users' email
            user = User.objects.get(id=user_info.user.id)
            user.email = email
            user.save()

    def get(self, request):
        # Create the user info if it does not exist yet
        # Because usually this view is called as soon as the user log in
        # Also required for other apps authorization

        # @NOTE: This needs to be redesigned as it causes a lot of queries
        user_info = get_or_create_user_info(request)

        # ------ PUT APP AUTHORIZATION HERE ------ #
        # This a good place to trigger creations of authorization models if they dont exist
        # Handle errors in the functions to return an empty {} to avoid failures here
        app_investigations = (
            investigations.permissions.get_or_create_investigation_authorization(
                "", as_dict=True, user_info_model=user_info
            )["model"]
        )
        # ------ BUILD RETURN CONTEXT HERE ------ #
        app_context = {"app_investigations": app_investigations}

        # Check if user is not confirmed
        # Check preauthorized users and if exists update informations and that 's it
        # To streamline users coming in to the dashboard
        if not user_info.confirmed_user:
            email = request.query_params.get("email")
            if email:
                self.perform_pre_authorized_user_check(email, user_info)

        return Response(
            {**model_to_dict(user_info), **app_context}, status=status.HTTP_200_OK
        )


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


@method_decorator(
    **{
        "name": "post",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "file",
                    in_=openapi.IN_FORM,
                    description="CSV File containing a list of energy data",
                    type=openapi.TYPE_FILE,
                    required=True,
                )
            ]
        ),
    }
)
class BulkCreateFacility(APIView):
    """
    Bulk create/update Facility
    Headers must be present with the following
    (facility_name, facility_identifier, postal_code, latitude, longitude, area, address, category_type, closed)
    category type must be "Retail" | "Warehouse"
    """

    parser_classes = [MultiPartParser]

    def post(self, request):
        if not request.user.is_superuser:
            return Response(
                {"message": "Only super users allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "file" in request.data:
            # Parse file
            data = parse_in_memory_csv(request.data["file"])

            if data:
                async_bulk_create_facility.delay(data)

        return Response(
            {"message": "Task created"},
            status=status.HTTP_201_CREATED,
        )
