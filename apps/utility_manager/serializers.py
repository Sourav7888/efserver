from rest_framework import serializers
from .models import UtilityBill


class UtilitySr(serializers.ModelSerializer):
    """
    Can be used to serialize data |Be aware of order by group by issue
    """

    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    display_date = serializers.SerializerMethodField()

    class Meta:
        model = UtilityBill
        fields = ("month", "year", "usage", "cost", "unit_cost", "display_date")

    def get_month(self, obj):
        return obj["billing_date__month"] if "billing_date__month" in obj else None

    def get_year(self, obj):
        return obj["billing_date__year"] if "billing_date__year" in obj else None

    def get_unit_cost(self, obj):
        return round(obj["unit_cost"], 3)

    def get_display_date(self, obj):
        return (
            f"{str(obj['billing_date__month']).zfill(2)}-{obj['billing_date__year']}"
            if "billing_date__month" in obj
            else None
        )
        return None
