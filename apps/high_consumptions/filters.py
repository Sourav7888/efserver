from django_filters import rest_framework as filters
from .models import HC, HCReportTracker


class HCFl(filters.FilterSet):
    hc_document = filters.CharFilter(field_name="hc_document", lookup_expr="icontains")

    class Meta:
        model = HC
        fields = "__all__"


class HCReportTrackerFl(filters.FilterSet):
    report_metadata = filters.CharFilter(
        field_name="report_metadata", lookup_expr="icontains"
    )

    class Meta:
        model = HCReportTracker
        fields = "__all__"
