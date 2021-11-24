from rest_framework.views import APIView
from apps.shared.parsers import parse_in_memory_csv
from apps.utility_manager.tasks import async_bulk_create_utility
from rest_framework.response import Response
from rest_framework import status
from .cs_schema import BulkCreateUtility
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser


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
