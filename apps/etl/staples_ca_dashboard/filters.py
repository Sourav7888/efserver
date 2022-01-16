from django_filters import rest_framework as filters
from .models import Renewables, LedList


class RenewablesFl(filters.FilterSet):
    class Meta:
        model = Renewables
        fields = "__all__"


class LedListFl(filters.FilterSet):
    class Meta:
        model = LedList
        fields = "__all__"
