from rest_framework.serializers import ModelSerializer
from .models import Renewables, LedList


class RenewablesSr(ModelSerializer):
    class Meta:
        model = Renewables
        fields = ("year", "purchased_energy", "emission_reduction")


class LedListSr(ModelSerializer):
    class Meta:
        model = LedList
        fields = "__all__"
