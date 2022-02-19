from .models import WeatherStation, WeatherData
from rest_framework import generics
from .serializers import WeatherStationSr, WeatherDataSr
from .pagination import WeatherStationPg, WeatherDataPg
from rest_framework.views import APIView
from rest_framework.response import Response
from .filters import WeatherDataFl
from .parsers import WeatherDataPr
from apps.shared.processors import group_and_sum
from rest_framework import status
from core.permissions import enforce_parameters
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .queries import query_coord_weather_data


class WeatherStationList(generics.ListAPIView):
    """
    Returns a list of all available weather stations, can be filtered.
    """

    serializer_class = WeatherStationSr
    filterset_fields = "__all__"
    pagination_class = WeatherStationPg

    def get_queryset(self):
        stations = WeatherStation.objects.all().order_by("climate_id")

        return stations


class WeatherDataDaily(generics.ListAPIView):
    """
    Returns a list of all available  weather data for a given climate identifier.Ref: 1017099
    """

    serializer_class = WeatherDataSr
    pagination_class = WeatherDataPg
    filterset_class = WeatherDataFl

    def get_queryset(self):
        data = WeatherData.objects.all().select_related("climate_id")

        return data


class WeatherDataMonthly(generics.ListAPIView):
    """
    Returns a list of all available monthly weather data for a given climate identifier.Ref: 1017099
    """

    serializer_class = WeatherDataSr
    filterset_class = WeatherDataFl

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if queryset.exists:
            df = WeatherDataPr(queryset=queryset).evaluate_queryset_to_df()
            if not df.empty:
                df = group_and_sum(df, year=True, month=True, group_by="date")
                df.reset_index(inplace=True)
                response = df.to_dict("records")
                return Response({"result": response}, status=status.HTTP_200_OK)

        return Response({"result": []}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return WeatherData.objects.all().select_related("climate_id")


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "latitude",
                    in_=openapi.IN_QUERY,
                    description="latitude",
                    type=openapi.TYPE_NUMBER,
                    required=True,
                ),
                openapi.Parameter(
                    "longitude",
                    in_=openapi.IN_QUERY,
                    description="longitude",
                    type=openapi.TYPE_NUMBER,
                    required=True,
                ),
            ],
        ),
    }
)
class GetWeatherDataByCoord(APIView):
    @method_decorator(enforce_parameters(params=["latitude", "longitude"]))
    def get(self, request):

        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except ValueError:
            return Response(
                {"error": "latitude and longitude must be numeric"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = query_coord_weather_data(latitude, longitude)
        # Must be transformed into a string as Timestamp is not json safe
        data["date"] = data["date"].astype(str)

        return Response({"result": data.to_dict("records")}, status=status.HTTP_200_OK)
