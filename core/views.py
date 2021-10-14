from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cs_schema import TestViewSc
from django.utils.decorators import method_decorator
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated


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
