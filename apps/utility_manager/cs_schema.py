from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

BulkCreateUtility = {
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

DivisionUtility = {
    "name": "get",
    "decorator": swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "division_name",
                in_=openapi.IN_QUERY,
                description="division",
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

FacilityUtility = {
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
