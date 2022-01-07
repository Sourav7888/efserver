from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInvestigationManager, IsInvestigator, HasInvestigationAccess
from .serializers import (
    CreateInvestigationSr,
    UpdateInvestigationSr,
    GetInvestigationsSr,
)
from .models import Investigation
from .filters import GetInvestigationsFl
from .paginations import GetInvestigationsPg


class CreateInvestigation(CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsInvestigationManager,
        HasInvestigationAccess,
    ]
    serializer_class = CreateInvestigationSr


class UpdateInvestigation(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsInvestigator, HasInvestigationAccess]
    serializer_class = UpdateInvestigationSr
    lookup_field = "investigation_id"
    queryset = Investigation.objects.all()


class GetInvestigations(ListAPIView):
    permission_classes = [IsAuthenticated, HasInvestigationAccess]
    serializer_class = GetInvestigationsSr
    queryset = Investigation.objects.all()
    filterset_class = GetInvestigationsFl
    pagination_class = GetInvestigationsPg
