from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from apps.reports.models import CustomerReport
from .cs_schema import CreateScorecard
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser
from apps.analytics.scorecard.scorecard_analytics import generate_scorecard
from rest_framework.response import Response
from .filters import CustomerReportFl
from .serializers import CustomerReportSr
from .paginations import CustomerReportPg

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


class GetCustomerReports(ListAPIView):
    # @NOTE: Soft check request body to make sure it doesnt fail if user_info
    # is not created yet
    permission_classes = [IsAuthenticated, CheckRequestBody]
    serializer_class = CustomerReportSr
    pagination_class = CustomerReportPg
    filterset_class = CustomerReportFl

    def get_queryset(self):
        return CustomerReport.objects.filter(
            customer=self.request.user.user_info.customer
        )
