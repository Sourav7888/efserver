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
from .cs_schema import BulkCreateWasteData


class GetWasteData(ListAPIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]
    queryset = WasteData.objects.all()
    serializer_class = WasteDataSr
    filterset_class = WasteDataFl
    pagination_class = WasteDataPg


@method_decorator(**BulkCreateWasteData)
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
