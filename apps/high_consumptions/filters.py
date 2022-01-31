from django_filters import rest_framework as filters
from .models import HC


class HCFl(filters.FilterSet):
    class Meta:
        model = HC
        fields = "__all__"
