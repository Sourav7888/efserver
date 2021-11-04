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
