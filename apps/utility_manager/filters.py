from django_filters import rest_framework as filters
from .models import TYPE_CHOICES, UtilityBill


class DivisionUtilityFl(filters.FilterSet):
    utility_type = filters.ChoiceFilter(choices=TYPE_CHOICES, required=True)
    min_date = filters.DateFilter(field_name="billing_date", lookup_expr="gte")
    max_date = filters.DateFilter(field_name="billing_date", lookup_expr="lte")

    class Meta:
        model = UtilityBill
        fields = [
            "utility_type",
            "min_date",
            "max_date",
        ]
