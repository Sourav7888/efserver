from .models import User
from rest_framework.serializers import ModelSerializer, RelatedField


class NameField(RelatedField):
    def to_representation(self, value):
        attr = [k for k in value.__dict__ if "name" in k][0]
        return getattr(value, attr)


class UserSr(ModelSerializer):
    platforms = NameField(many=True, read_only=True)
    roles = NameField(many=True, read_only=True)
    permissions = NameField(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"
