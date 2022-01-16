from django_filters import rest_framework as filters
from .models import Renewables


class RenewablesFl(filters.FilterSet):
    class Meta:
        model = Renewables
        fields = "__all__"
