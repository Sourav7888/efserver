from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cs_staples_ca import schema


class GetStaplesSwaggerSchema(APIView):
    permission_classes = []

    def get(self, request):
        return Response(schema, status=status.HTTP_200_OK)
