from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from authorization_server.serializers import UserSr
from .models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
from rest_framework.response import Response


class GetUserInfo(RetrieveAPIView):
    """
    Get user info
    """

    permission_classes = [IsAuthenticated, IsSuperUser]
    lookup_field = "user_id"
    queryset = User.objects.all()
    serializer_class = UserSr


class GetMyInfo(APIView):
    """
    Get my info
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSr

    def get(self, request):
        request_user = self.request.user.user_info.user_id
        model = get_object_or_404(User, user_id=request_user)
        serializer = self.serializer_class(model)
        return Response(serializer.data)


# @TODO: Add a pre-authorized handler to make it possible for
# New users to come through without prior existence
