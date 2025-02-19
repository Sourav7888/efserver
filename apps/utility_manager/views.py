from rest_framework.views import APIView
from apps.shared.parsers import parse_in_memory_csv
from apps.utility_manager.tasks import async_bulk_create_utility
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import ListAPIView
from .models import UtilityBill
from core.models import Facility, Division
from .serializers import UtilitySr
from .paginations import UtilityPg
from .filters import UtilityFl
from core.permissions import CheckRequestBody, enforce_parameters, IsSuperUser
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
                    "timeframe",
                    in_=openapi.IN_QUERY,
                    description="yearly | monthly",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class GetFacilityUtility(ListAPIView):
    """
    List all utility for a facility
    """

    filterset_class = UtilityFl
    serializer_class = UtilitySr
    pagination_class = UtilityPg
    permission_classes = [IsAuthenticated, CheckRequestBody]

    @method_decorator(enforce_parameters(params=["timeframe", "facility_name"]))
    def list(self, request, *args, **kwargs):
        if request.GET["timeframe"].lower() == "monthly":
            return super().list(self, request, *args, **kwargs)

        # Overriding for yearly due to an issue where group by is required yet if not
        # Grouped by start date will fail regardless of the pagination
        # To fix in the future
        elif request.GET["timeframe"].lower() == "yearly":
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

            results = [{"display_date": x["year"].year, **x} for x in queryset]

            return Response({"results": results}, status=status.HTTP_200_OK)

        else:
            return Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):

        facility = Facility.objects.get(facility_name=self.request.GET["facility_name"])
        if self.request.GET["timeframe"].lower() == "yearly":
            return UtilityBill.yearly.filter(facility=facility)
        elif self.request.GET["timeframe"].lower() == "monthly":
            # @TODO: Possibly use object here but change the serializer conditionaly
            return UtilityBill.monthly.filter(facility=facility)
        else:
            return None


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division_name",
                    in_=openapi.IN_QUERY,
                    description="division_name",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "timeframe",
                    in_=openapi.IN_QUERY,
                    description="yearly | monthly",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class GetDivisionUtility(ListAPIView):
    """
    Get all utilities for a Division
    """

    serializer_class = UtilitySr
    pagination_class = UtilityPg
    filterset_class = UtilityFl
    permission_classes = [IsAuthenticated, CheckRequestBody]

    @method_decorator(enforce_parameters(params=["timeframe", "division_name"]))
    def list(self, request, *args, **kwargs):
        if request.GET["timeframe"].lower() == "monthly":
            return super().list(self, request, *args, **kwargs)

        # Overriding for yearly due to an issue where group by is required yet if not
        # Grouped by start date will fail regardless of the pagination
        # To fix in the future
        elif request.GET["timeframe"].lower() == "yearly":
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

            results = [{"display_date": x["year"].year, **x} for x in queryset]

            return Response({"results": results}, status=status.HTTP_200_OK)

        else:
            return Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if "division_name" not in self.request.GET:
            return UtilityBill.objects.none()
        division = Division.objects.get(division_name=self.request.GET["division_name"])
        facilities = Facility.objects.filter(division=division)
        if self.request.GET["timeframe"].lower() == "yearly":
            return UtilityBill.yearly.filter(facility__in=facilities)
        elif self.request.GET["timeframe"].lower() == "monthly":
            return UtilityBill.monthly.filter(facility__in=facilities)
        else:
            return UtilityBill.objects.none()


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division_name",
                    in_=openapi.IN_QUERY,
                    description="division_name",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "timeframe",
                    in_=openapi.IN_QUERY,
                    description="yearly | monthly",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class GetPublicDivisionUtility(ListAPIView):
    """
    Get all utilities for a Division
    """

    serializer_class = UtilitySr
    pagination_class = UtilityPg
    filterset_class = UtilityFl
    permission_classes = []

    @method_decorator(enforce_parameters(params=["timeframe", "division_name"]))
    def list(self, request, *args, **kwargs):
        if request.GET["timeframe"].lower() == "monthly":
            queryset = self.filter_queryset(self.get_queryset())

            results = []
            if not queryset:
                Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

            # Removing the cost cost here
            for x in queryset:
                results.append(
                    {
                        "display_date": f"{x['billing_date__month']}-{x['billing_date__year']}",
                        "utility_type": x["utility_type"],
                        "usage": x["usage"],
                        "month": x["billing_date__month"],
                        "year": x["billing_date__year"],
                    }
                )

            return Response({"results": results}, status=status.HTTP_200_OK)

        # Overriding for yearly due to an issue where group by is required yet if not
        # Grouped by start date will fail regardless of the pagination
        # To fix in the future
        elif request.GET["timeframe"].lower() == "yearly":
            queryset = self.filter_queryset(self.get_queryset())

            results = []
            if not queryset:
                Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

            # Removing the cost cost here
            for x in queryset:
                results.append(
                    {
                        "display_date": x["year"].year,
                        "utility_type": x["utility_type"],
                        "year": x["year"],
                        "usage": x["usage"],
                    }
                )

            return Response({"results": results}, status=status.HTTP_200_OK)

        else:
            return Response({"Invalid timeframe"}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if "division_name" not in self.request.GET:
            return UtilityBill.objects.none()
        division = Division.objects.get(division_name=self.request.GET["division_name"])
        facilities = Facility.objects.filter(division=division)
        if self.request.GET["timeframe"].lower() == "yearly":
            return UtilityBill.yearly.filter(facility__in=facilities)
        elif self.request.GET["timeframe"].lower() == "monthly":
            return UtilityBill.monthly.filter(facility__in=facilities)
        else:
            return UtilityBill.objects.none()


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
class BulkCreateUtility(APIView):
    """
    Bulk create/update utility
    Cols must be:
    (facility, billing_date, utility_type, cost, usage, unit, billing_days)
    """

    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):

        if "file" in request.data:
            # Parse file
            data = parse_in_memory_csv(request.data["file"])

            if data:
                async_bulk_create_utility.delay(data)

        return Response(
            {"message": "Task created"},
            status=status.HTTP_201_CREATED,
        )
