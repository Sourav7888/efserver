from rest_framework.serializers import ModelSerializer
from .models import Renewables


class RenewablesSr(ModelSerializer):
    class Meta:
        model = Renewables
        fields = "__all__"
