from .models import HC
from rest_framework.serializers import ModelSerializer


class HCSr(ModelSerializer):
    class Meta:
        model = HC
        fields = "__all__"
