from django_filters import rest_framework as filters
from .models import CustomerReport


class CustomerReportFl(filters.FilterSet):
    class Meta:
        model = CustomerReport
        fields = ["created_at"]
