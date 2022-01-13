from rest_framework.views import APIView
from apps.shared.parsers import parse_in_memory_csv
from apps.utility_manager.tasks import async_bulk_create_utility
from rest_framework.response import Response
from rest_framework import status
from .cs_schema import BulkCreateUtility
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import ListAPIView
from .models import UtilityBill
from core.models import Facility, Division
from .serializers import UtilitySr
from .paginations import UtilityPg
from .filters import UtilityFl
from .cs_schema import DivisionUtility, FacilityUtility
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated


@method_decorator(**FacilityUtility)
class GetFacilityUtility(ListAPIView):
    """
    List all utility for a facility
    """

    filterset_class = UtilityFl
    serializer_class = UtilitySr
    pagination_class = UtilityPg
    permission_classes = [IsAuthenticated, CheckRequestBody]

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


@method_decorator(**DivisionUtility)
class GetDivisionUtility(ListAPIView):
    """
    Get all utilities for a Division
    """

    serializer_class = UtilitySr
    pagination_class = UtilityPg
    filterset_class = UtilityFl
    permission_classes = [IsAuthenticated, CheckRequestBody]

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


@method_decorator(**BulkCreateUtility)
class BulkCreateUtility(APIView):
    """
    Bulk create/update utility
    Cols must be:
    (facility, billing_date, utility_type, cost, usage, unit, billing_days)
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
                async_bulk_create_utility.delay(data)

        return Response(
            {"message": "Task created"},
            status=status.HTTP_201_CREATED,
        )
