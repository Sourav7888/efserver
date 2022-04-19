from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from authorization_server.serializers import UserSr
from .models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser


class GetUserInfo(RetrieveAPIView):
    """
    Get user info
    """

    permission_classes = [IsAuthenticated, IsSuperUser]
    lookup_field = "user_id"
    queryset = User.objects.all()
    serializer_class = UserSr


class GetMyInfo(RetrieveAPIView):
    """
    Get my info
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSr

    def get_queryset(self):
        return get_object_or_404(User, user_id=self.request.user.user_id)


# @TODO: Add a pre-authorized handler to make it possible for
# New users to come through without prior existence
