from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cs_schema import TestViewSc
from django.utils.decorators import method_decorator
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated
from .permissions import get_or_create_user_info
from rest_framework.generics import RetrieveAPIView
from .serializers import UserInfoSr


@method_decorator(
    **TestViewSc,
)
class CoreTestView(APIView):
    """
    Dummy to test permission class # Do Not Use!
    """

    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get(self, request):
        return Response({"message": "hello world"}, status=status.HTTP_200_OK)


class UserPermission(RetrieveAPIView):
    """
    Return the user permissions across modules
    """

    serializer_class = UserInfoSr

    def get_object(self):
        # Create the user info if it does not exist yet
        # Because usually this view is called as soon as the user log in
        user_info = get_or_create_user_info(self.request)
        return user_info
