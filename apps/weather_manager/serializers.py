from rest_framework import serializers
from .models import WeatherStation, WeatherData


class WeatherStationSr(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = "__all__"


class WeatherDataSr(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = "__all__"
