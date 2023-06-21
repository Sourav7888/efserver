from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Renewables, LedList, BillAudit
from .serializers import RenewablesSr, LedListSr, BillAuditSr
from .filters import RenewablesFl, LedListFl, BillAuditFl
from .paginations import RenewablesPg, LedListPg, BillAuditPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
# @TODO Override list so that to make sure the bug groupby is fixed
class GetRenewablesYearly(ListAPIView):
    # @CHANGES permission_classes = [IsAuthenticated]
    permission_classes = []
    queryset = Renewables.yearly.all()
    serializer_class = RenewablesSr
    filterset_class = RenewablesFl
    pagination_class = RenewablesPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
class GetLedList(ListAPIView):
    # @CHANGES permission_classes = [IsAuthenticated]
    permission_classes = []
    queryset = LedList.objects.all()
    serializer_class = LedListSr
    filterset_class = LedListFl
    pagination_class = LedListPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
class GetBillAudit(ListAPIView):
    # @CHANGES permission_classes = [IsAuthenticated]
    permission_classes = []
    queryset = BillAudit.objects.all()
    serializer_class = BillAuditSr
    filterset_class = BillAuditFl
    pagination_class = BillAuditPg
