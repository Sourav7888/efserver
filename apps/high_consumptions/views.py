from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from .tasks import generate_hc_report_by_facility
from core.models import Facility
from .base import ElectricityHighConsumption, NaturalGasHighConsumption


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
class GenerateHCReport(APIView):
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"message": "You are not authorized to access this resource"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
        elif request.GET["utility_type"] == "natural_gas":
            report_id = generate_hc_report_by_facility(
                facility,
                NaturalGasHighConsumption,
                request.GET["investigation_date"],
                facility_context=True,
                stats_context=True,
            )
        else:
            return Response(
                {"message": "Invalid utility type"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"report_id": report_id}, status=status.HTTP_200_OK)
