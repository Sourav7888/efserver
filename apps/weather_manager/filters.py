from django_filters import rest_framework as filters
from .models import WeatherData


class WeatherDataFl(filters.FilterSet):
    min_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    max_date = filters.DateFilter(field_name="date", lookup_expr="lte")
    climate_id = filters.CharFilter(field_name="climate_id", required=True)

    class Meta:
        model = WeatherData
        fields = ["climate_id", "min_date", "max_date"]
