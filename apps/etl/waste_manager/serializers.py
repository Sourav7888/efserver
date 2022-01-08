from rest_framework import serializers
from .models import WasteData


class WasteDataSr(serializers.ModelSerializer):
    class Meta:
        model = WasteData
        fields = "__all__"
