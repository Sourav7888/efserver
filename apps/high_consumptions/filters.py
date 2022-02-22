from django_filters import rest_framework as filters
from .models import HC


class HCFl(filters.FilterSet):
    hc_document = filters.CharFilter(field_name="hc_document", lookup_expr="icontains")

    class Meta:
        model = HC
        fields = "__all__"
