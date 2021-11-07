from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import generate_gas_high_consumption


class TestView(APIView):
    def get(self, request):
        return Response(generate_gas_high_consumption("2021-07-01"))
