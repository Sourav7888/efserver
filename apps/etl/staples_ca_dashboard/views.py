from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Renewables
from .serializers import RenewablesSr
from .filters import RenewablesFl
from .paginations import RenewablesPg


# THis view is not critical
# @TODO Add extra checks to ensure other users that are not from staples can access
class GetRenewables(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Renewables.objects.all()
    serializer_class = RenewablesSr
    filterset_class = RenewablesFl
    pagination_class = RenewablesPg
