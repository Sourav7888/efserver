from rest_framework.serializers import ModelSerializer
from .models import Renewables, LedList


class RenewablesSr(ModelSerializer):
    class Meta:
        model = Renewables
        fields = "__all__"


class LedListSr(ModelSerializer):
    class Meta:
        model = LedList
        fields = "__all__"
