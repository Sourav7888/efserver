from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Renewables, LedList
from .serializers import RenewablesSr, LedListSr
from .filters import RenewablesFl, LedListFl
from .paginations import RenewablesPg, LedListPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
class GetRenewables(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Renewables.objects.all()
    serializer_class = RenewablesSr
    filterset_class = RenewablesFl
    pagination_class = RenewablesPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
class GetLedList(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = LedList.objects.all()
    serializer_class = LedListSr
    filterset_class = LedListFl
    pagination_class = LedListPg
