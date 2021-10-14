from .models import UserInfo
from rest_framework.serializers import ModelSerializer


class UserInfoSr(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"
