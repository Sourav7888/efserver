from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TestView(APIView):
    def get(self, request):
        print(request.user.username)
        print(request.GET)
        return Response({"message": "hello world"}, status=status.HTTP_200_OK)
