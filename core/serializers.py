from .models import UserInfo, Division, Facility
from rest_framework.serializers import ModelSerializer


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
