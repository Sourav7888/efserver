from .tasks import async_bulk_create_waste_data
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.permissions import CheckRequestBody, IsSuperUser
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
from core.permissions import enforce_parameters
from apps.shared.processors import check_date_format
from apps.shared.cs_exceptions import InvalidDateFormat
from django.db.models import Q
from core.models import Facility, Customer


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
    # @CHANGES permission_classes = [IsAuthenticated, CheckRequestBody]
    permission_classes = []
    serializer_class = WasteDataSr
    filterset_class = WasteDataFl
    pagination_class = WasteDataPg

    @method_decorator(enforce_parameters(params=["division"]))
    def list(self, request, *args, **kwargs):
        # @NOTE: Overriding due to issue with group by making the annotation not working
        queryset = self.filter_queryset(self.get_queryset())

        results = [
            {**x, "display_date": str(x["year"]).split("-")[0]} for x in queryset
        ]

        return Response({"results": results}, status=status.HTTP_200_OK)

    def get_queryset(self):

        # @TODO: This is not good this needs to not depend on validate_facility_access
        # Rather filter by the division since all dashboard users need all the available data aggregated
        # facilities = validate_facility_access(self.request).filter(
        #     division=self.request.GET["division"]
        # )

        facilities = Facility.objects.filter(
            division__customer=Customer.objects.get(customer_name="Staples CA")
        ).select_related("division")
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
                openapi.Parameter(
                    "min_date",
                    in_=openapi.IN_QUERY,
                    description="min_date",
                    type=openapi.TYPE_STRING,
                    required=False,
                ),
            ]
        ),
    }
)
class GetWasteTotalFromStart(APIView):
    # @CHANGES: permission_classes = [IsAuthenticated, CheckRequestBody]
    permission_classes = []

    @method_decorator(enforce_parameters(params=["division", "waste_category"]))
    def get(self, request):
        try:
            facilities = Facility.objects.filter(division=request.GET["division"])

            # @NOTE: Adding this for for arbitrary date and diversion filtering
            kwargs = {"is_recycled": True}

            # @NOTE: if diversion meaning that all is not recycled but diverted hence
            # whether recycled is true or not we still want that value usually it is set to false
            if "diversion" in request.GET:
                diverted = bool(strtobool(request.GET["diversion"]))
                if diverted:
                    kwargs.pop("is_recycled")

            if "min_date" in request.GET:
                try:
                    kwargs["pickup_date__gte"] = check_date_format(
                        request.GET["min_date"]
                    )
                except InvalidDateFormat:
                    return Response(
                        {"message": "Invalid date format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            data = WasteData.yearly.filter(
                facility__in=facilities,
                waste_category=request.GET["waste_category"],
                **kwargs,
            ).aggregate(Sum("weight"))["weight__sum"]

        except Exception as error:
            return Response(
                {"message": "Something went wrong, Please check your request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"total": data if data else 0}, status=status.HTTP_200_OK)


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
    # @CHANGES permission_classes = [IsAuthenticated, CheckRequestBody]
    permission_classes = []

    @method_decorator(enforce_parameters(params=["division", "year", "waste_category"]))
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
    # @CHANGES permission_classes = [IsAuthenticated, CheckRequestBody]
    permission_classes = []

    @method_decorator(enforce_parameters(params=["division", "waste_category"]))
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
            return Response(
                {"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"recycling_rate": recycling_rate}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "unit",
                    in_=openapi.IN_QUERY,
                    description="mt or kg",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "min_year",
                    in_=openapi.IN_QUERY,
                    description="starting year of calculation",
                    type=openapi.TYPE_INTEGER,
                    required=True,
                ),
            ]
        ),
    }
)
class GetTotalAllCategory(APIView):
    @method_decorator(enforce_parameters(params=["unit", "min_year"]))
    def get(self, request):
        if request.GET["unit"] not in ["mt", "kg"]:
            return Response(
                {"message": "Invalid unit"}, status=status.HTTP_400_BAD_REQUEST
            )

        unit = request.GET["unit"]

        facilities = Facility.objects.filter(
            division__customer=request.user.user_info.customer
        )
        data = WasteData.yearly.filter(
            Q(is_recycled=True) | Q(is_diverted=True),
            facility__in=facilities,
            unit="mt",
            pickup_date__year__gte=request.GET["min_year"],
        )

        total = data.aggregate(Sum("weight"))["weight__sum"]

        if not total:
            total = 0

        if unit == "kg":
            total = total * 1000

        return Response({"total": total, "unit": unit}, status=status.HTTP_200_OK)


@method_decorator(
    **{
        "name": "post",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "file",
                    in_=openapi.IN_FORM,
                    description="(pickup_date, facility, waste_name, weight, is_recycled, waste_category, provided_by, is_diverted, unit)",
                    type=openapi.TYPE_FILE,
                    required=True,
                )
            ]
        ),
    }
)
class BulkCreateWasteData(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):

        if "file" in request.data:
            # Parse file
            data = parse_in_memory_csv(request.data["file"])

            if data:
                async_bulk_create_waste_data.delay(data)

        return Response(
            {"message": "Task created"},
            status=status.HTTP_201_CREATED,
        )
