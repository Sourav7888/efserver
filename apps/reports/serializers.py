from rest_framework import serializers
from .models import CustomerReport


class CustomerReportSr(serializers.ModelSerializer):
    class Meta:
        model = CustomerReport
        fields = "__all__"
