from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


BulkCreateWasteData = {
    "name": "post",
    "decorator": swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="CSV File containing a list of waste data",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ]
    ),
}
