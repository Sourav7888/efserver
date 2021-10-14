from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


TestViewSc = {
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
