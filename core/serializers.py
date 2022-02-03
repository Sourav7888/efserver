from .models import UserInfo, Division, Facility
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class DivisionSr(ModelSerializer):
    class Meta:
        model = Division
        fields = "__all__"


class FacilitySr(ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"


class UserInfoSr(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"


def model_to_dict(instance) -> dict:
    """
    Convert a model instance to dict.
    """

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = type(instance)
            fields = "__all__"

    data = Serializer(instance).data
    # convert from ordered dict to dict
    return dict(data)
