from rest_framework.response import Response
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.permissions import CheckRequestBody
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UtilityBill
from core.models import Facility
import pandas as pd
from apps.analytics.scorecard.scorecard_analytics import ScoreCardDf


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division_name",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
                openapi.Parameter(
                    "utility_type",
                    in_=openapi.IN_QUERY,
                    description="utility_type",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class CalculateTotalEnergyReduction(APIView):
    permission_classes = [IsAuthenticated, CheckRequestBody]

    def get_data(self, request) -> pd.DataFrame:
        facilities = Facility.objects.filter(division=request.GET["division_name"])
        utility_type = request.GET["utility_type"]

        return pd.DataFrame(
            list(
                UtilityBill.yearly.filter(
                    facility__in=facilities, utility_type=utility_type
                )
            )
        )

    def get(self, request):
        # @TODO: This needs to be cleaned up
        for x in ["utility_type", "division_name"]:
            if x not in request.GET:
                return Response({"Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        data = self.get_data(request)

        return Response(
            {
                # @TODO: Need a test?
                "result": {
                    "usage_reduction": round(data["usage"].diff().sum(), 2),
                    "cost_reduction": round(data["cost"].diff().sum(), 2),
                    "average_unit_cost": round(data["unit_cost"].mean(), 2),
                }
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(
    **{
        "name": "get",
        "decorator": swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    "division_name",
                    in_=openapi.IN_QUERY,
                    description="division",
                    type=openapi.TYPE_STRING,
                    required=True,
                ),
            ],
        ),
    }
)
class CalculateDivisionGhgAvgPf(APIView):
    """
    Returns the average ghg emission for a division per facility per month
    """

    permission_classes = [IsAuthenticated, CheckRequestBody]

    def calculate_sum_ghg(self, df: pd.DataFrame) -> pd.DataFrame:
        total = df.groupby(["date"])["ghg (MT)"].sum().reset_index()
        return total

    def get(self, request):
        # @TODO: This needs to be cleaned up
        for x in ["division_name"]:
            if x not in request.GET:
                return Response({"Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        scorecard = ScoreCardDf(request.GET["division_name"])
        data = self.calculate_sum_ghg(scorecard.avg_facility_usg_per_month())

        return Response({"result": data.to_dict("records")}, status=status.HTTP_200_OK)
