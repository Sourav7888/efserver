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
from .serializers import DivisionUtilitySr
from .paginations import DivisionUtilityPg
from .filters import DivisionUtilityFl
from .cs_schema import DivisionUtility
from core.permissions import CheckRequestBody


@method_decorator(**DivisionUtility)
class GetDivisionUtility(ListAPIView):
    """
    Get all utilities for a Division
    """

    serializer_class = DivisionUtilitySr
    pagination_class = DivisionUtilityPg
    filterset_class = DivisionUtilityFl

    def list(self, request, *args, **kwargs):
        # Check here otherwise swagger will not display the endpoint
        perm = CheckRequestBody()
        if not perm.has_division_permission(request, request.GET):
            return Response(
                {"message": "You are not allowed to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

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
        division = Division.objects.get(division_name=self.request.GET["division_name"])
        facilities = Facility.objects.filter(division=division)
        if self.request.GET["timeframe"].lower() == "yearly":
            return UtilityBill.yearly.filter(facility__in=facilities)
        elif self.request.GET["timeframe"].lower() == "monthly":
            return UtilityBill.monthly.filter(facility__in=facilities)
        else:
            return None


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
            {"message": "Task created will notify tantely.raza@enerfrog.com"},
            status=status.HTTP_201_CREATED,
        )
