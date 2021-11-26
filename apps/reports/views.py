from rest_framework.views import APIView
from .cs_schema import CreateScorecard
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from apps.analytics.scorecard.scorecard_analytics import generate_scorecard
from rest_framework.response import Response


# @TODO: This is supposed to be an async funtion with report
@method_decorator(**CreateScorecard)
class CreateScorecard(APIView):
    """
    Will create an instance of report
    and attach a json file of the scorecard data - will return the report id
    """

    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated, CheckRequestBody]

    def post(self, request):
        req = request.POST
        data = generate_scorecard(req["division_name"], req["month"], req["year"])
        return Response(data)
