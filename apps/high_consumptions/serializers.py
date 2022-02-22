from .models import HC
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class HCSr(ModelSerializer):
    class Meta:
        model = HC
        fields = "__all__"


class CustomSchema(serializers.Serializer):
    utility_type = serializers.CharField(max_length=100)
    division = serializers.CharField(max_length=100)
    investigation_date = serializers.DateField()
