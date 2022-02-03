from rest_framework.serializers import ModelSerializer
from .models import Renewables, LedList, BillAudit


class RenewablesSr(ModelSerializer):
    class Meta:
        model = Renewables
        fields = ("year", "purchased_energy", "emission_reduction")


class LedListSr(ModelSerializer):
    class Meta:
        model = LedList
        fields = "__all__"


class BillAuditSr(ModelSerializer):
    class Meta:
        model = BillAudit
        fields = "__all__"
