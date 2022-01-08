from django_filters import rest_framework as filters
from .models import WasteData


class WasteDataFl(filters.FilterSet):
    class Meta:
        model = WasteData
        fields = "__all__"
