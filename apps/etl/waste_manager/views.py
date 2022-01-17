from .tasks import async_bulk_create_waste_data
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.permissions import CheckRequestBody
from .models import WasteData
from .serializers import WasteDataSr
from .paginations import WasteDataPg
from .filters import WasteDataFl
from rest_framework.parsers import MultiPartParser
from apps.shared.parsers import parse_in_memory_csv
from rest_framework import status
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.permissions import validate_facility_access


class GetWasteData(ListAPIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]
    serializer_class = WasteDataSr
    filterset_class = WasteDataFl
    pagination_class = WasteDataPg

    def get_queryset(self):
        facilities = validate_facility_access(self.request)
        return (
            WasteData.objects.filter(facility__in=facilities)
            .select_related("facility")
            .select_related("provided_by")
            .select_related("waste_category")
        )


class GetWasteDataYearly(ListAPIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]
    serializer_class = WasteDataSr
    filterset_class = WasteDataFl
    pagination_class = WasteDataPg

    def list(self, request, *args, **kwargs):
        # @NOTE: Overriding due to issue with group by making the annotation not working
        queryset = self.filter_queryset(self.get_queryset())

        results = [
            {**x, "display_date": str(x["year"]).split("-")[0]} for x in queryset
        ]

        return Response({"results": results}, status=status.HTTP_200_OK)

    def get_queryset(self):
        facilities = validate_facility_access(self.request)
        data = WasteData.yearly.filter(facility__in=facilities)

        return data


@method_decorator(
    **{
        "name": "post",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "file",
                    in_=openapi.IN_FORM,
                    description="(pickup_date, facility, waste_name, weight, is_recycled, waste_category, provided_by) ",
                    type=openapi.TYPE_FILE,
                    required=True,
                )
            ]
        ),
    }
)
class BulkCreateWasteData(APIView):
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
                async_bulk_create_waste_data.delay(data)

        return Response(
            {"message": "Task created"},
            status=status.HTTP_201_CREATED,
        )
