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
from core.models import Facility
from django.db.models import Sum
from distutils.util import strtobool


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


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                )
            ]
        ),
    }
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
        facilities = validate_facility_access(self.request).filter(
            division=self.request.GET["division"]
        )
        data = WasteData.yearly.filter(facility__in=facilities)

        return data


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "waste_category",
                    in_=openapi.IN_QUERY,
                    description="waste_category",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "diversion",
                    in_=openapi.IN_QUERY,
                    description="diversion",
                    type=openapi.TYPE_BOOLEAN,
                    required=False,
                ),
            ]
        ),
    }
)
class GetWasteTotalFromStart(APIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get(self, request):
        try:
            facilities = Facility.objects.filter(division=request.GET["division"])

            is_recycled = True
            # @NOTE: if diversion meaning that all is not recycled but diverted hebce
            # We can use non recycled as recycled
            # Maybe add to moldes diverted this is a quick fix
            if "diversion" in request.GET:
                is_recycled = not bool(strtobool(request.GET["diversion"]))

            data = WasteData.yearly.filter(
                facility__in=facilities,
                waste_category=request.GET["waste_category"],
                is_recycled=is_recycled,
            ).aggregate(Sum("weight"))
        except Exception as error:
            print(error)
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"total": data["weight__sum"]}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "waste_category",
                    in_=openapi.IN_QUERY,
                    description="waste_category",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "year",
                    in_=openapi.IN_QUERY,
                    description="year",
                    type=openapi.TYPE_INTEGER,
                    required=True,
                ),
            ]
        ),
    }
)
class GetWasteContributionByName(APIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get(self, request):
        try:
            division = self.request.GET["division"]
            year = self.request.GET["year"]
            waste_category = self.request.GET["waste_category"]

            facilities = Facility.objects.filter(division=division)

            query = (
                WasteData.objects.filter(
                    facility__in=facilities,
                    pickup_date__year=year,
                    waste_category=waste_category,
                )
                .values("pickup_date__year", "waste_name")
                .annotate(
                    weight=Sum("weight"),
                )
            )

            total = query.aggregate(Sum("weight"))["weight__sum"]

            data = [
                {
                    "waste_name": x["waste_name"],
                    "contrib": round(x["weight"] * 100 / total, 2),
                    "weight": x["weight"],
                    "year": x["pickup_date__year"],
                }
                for x in query
            ]

        except Exception as error:
            print(error)
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"results": data}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "waste_category",
                    in_=openapi.IN_QUERY,
                    description="waste_category",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ]
        ),
    }
)
class GetRecyclingRate(APIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get(self, request):
        try:
            facilities = Facility.objects.filter(division=request.GET["division"])
            data = WasteData.yearly.filter(
                facility__in=facilities,
                waste_category=request.GET["waste_category"],
            )

            recycling_rate = 0
            if data.exists():
                total = data.aggregate(Sum("weight"))["weight__sum"]
                recycled = data.filter(is_recycled=True).aggregate(Sum("weight"))[
                    "weight__sum"
                ]

                if recycled and total > 0:
                    recycling_rate = recycled * 100 / total

        except Exception as error:
            print(error)
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"recycling_rate": recycling_rate}, status=status.HTTP_200_OK)


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
