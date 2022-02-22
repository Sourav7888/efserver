import uuid
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from apps.investigations.permissions import (
    HasInvestigationAccess,
    IsInvestigationManager,
)
from core.permissions import CheckRequestBody, IsSuperUser
from .tasks import generate_hc_by_division, generate_hc_report_by_facility, generate_hc
from core.models import Facility
from .base import ElectricityHighConsumption, GasHighConsumption
from rest_framework.generics import ListAPIView
from .models import HC, HCReportTracker
from .serializers import HCSr, CustomSchema
from .filters import HCFl
from .paginations import HCPg
from core.permissions import enforce_parameters
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "facility",
                    in_=openapi.IN_QUERY,
                    description="facility",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "utility_type",
                    in_=openapi.IN_QUERY,
                    description="electricity or natural gas",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "investigation_date",
                    in_=openapi.IN_QUERY,
                    description="date",
                    type=openapi.TYPE_STRING,
                    required=True,
                    format=openapi.FORMAT_DATE,
                    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                ),
            ],
        ),
    }
)
class GenerateHCReportByFacility(APIView):
    """
    Generates a high consumption report for a single facility
    """

    permission_classes = [
        IsAuthenticated,
        IsInvestigationManager,
        HasInvestigationAccess,
    ]

    @method_decorator(
        enforce_parameters(params=["facility", "utility_type", "investigation_date"])
    )
    def get(self, request):
        facility = Facility.objects.filter(facility_name=request.GET["facility"])

        if not facility.exists():
            return Response(
                {"message": "Facility does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        facility = facility[0]

        if request.GET["utility_type"] == "electricity":
            # @NOTE: Should be made async if it causes issues
            report_id = generate_hc_report_by_facility(
                facility,
                ElectricityHighConsumption,
                request.GET["investigation_date"],
                facility_context=True,
            )
        elif request.GET["utility_type"] == "natural gas":
            report_id = generate_hc_report_by_facility(
                facility,
                GasHighConsumption,
                request.GET["investigation_date"],
                facility_context=True,
                stats_context=True,
            )
        else:
            return Response(
                {"message": "Invalid utility type"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"report_id": report_id}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "utility_type",
                    in_=openapi.IN_QUERY,
                    description="electricity or natural gas",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "investigation_date",
                    in_=openapi.IN_QUERY,
                    description="date",
                    type=openapi.TYPE_STRING,
                    required=True,
                    format=openapi.FORMAT_DATE,
                    pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                ),
            ],
        ),
    }
)
class GenerateHC(APIView):
    """
    Calculates High consumptions for all facilities
    """

    permission_classes = [IsAuthenticated, IsSuperUser]

    def get(self, request):

        _id = uuid.uuid4()

        if request.GET["utility_type"] == "electricity":
            # @NOTE: Should be made async if it causes issues
            generate_hc.delay(
                request.GET["utility_type"],
                request.GET["investigation_date"],
                _id,
            )
        elif request.GET["utility_type"] == "natural gas":
            generate_hc.delay(
                request.GET["utility_type"],
                request.GET["investigation_date"],
                _id,
            )
        else:
            return Response(
                {"message": "Invalid utility type"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"hc_id": _id}, status=status.HTTP_200_OK)


class GetGeneratedHC(ListAPIView):
    """
    Get Generated
    """

    permission_classes = [IsAuthenticated, IsSuperUser]

    serializer_class = HCSr
    filter_class = HCFl
    pagination_class = HCPg
    queryset = HC.objects.all()


@method_decorator(
    **{
        "name": "post",
        "decorator": swagger_auto_schema(
            request_body=CustomSchema,
            responses={200: "string"},
        ),
    }
)
class GenerateHCByDivision(APIView):
    """
    Generate high consumption by division and it creates a list of hc
    with autogenerated high consumption documents

    Must be able to add a field that says if there is already an investigation of that type
    in the system
    """

    permission_classes = [
        IsAuthenticated,
        IsInvestigationManager,
        HasInvestigationAccess,
        CheckRequestBody,
    ]

    @method_decorator(
        enforce_parameters(params=["division", "utility_type", "investigation_date"])
    )
    def post(self, request):

        if request.data["utility_type"] not in ["electricity", "natural gas"]:
            return Response(
                {"message": "Invalid utility type"}, status=status.HTTP_400_BAD_REQUEST
            )


        # Id used for the hc
        _id = str(uuid.uuid4())

        # Create a report so that when the process is finished we can call is ready on
        # The report models
        HCReportTracker.objects.create(hc_report_id=_id, creator=request.user.user_info)

        generate_hc_by_division.delay(
            _id,
            request.data["division"],
            request.data["utility_type"],
            request.data["investigation_date"],
        )

        return Response({"id": _id}, status=status.HTTP_200_OK)
