from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

CreateScorecard = {
    "name": "post",
    "decorator": swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "division_name",
                in_=openapi.IN_FORM,
                description="division_name",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "month",
                in_=openapi.IN_FORM,
                description="month",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "year",
                in_=openapi.IN_FORM,
                description="year",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ]
    ),
}
