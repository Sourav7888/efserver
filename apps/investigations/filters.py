from django_filters import rest_framework as filters
from .models import Investigation


class GetInvestigationsFl(filters.FilterSet):
    open_investigation = filters.BooleanFilter(
        field_name="investigation_investigator", lookup_expr="isnull"
    )

    class Meta:
        model = Investigation
        fields = "__all__"
