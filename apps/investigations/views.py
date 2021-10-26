from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInvestigationManager, IsInvestigator
from .serializers import CreateInvestigationSr, UpdateInvestigationSr
from .models import Investigation


class CreateInvestigation(CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsInvestigationManager,
    ]
    serializer_class = CreateInvestigationSr


class UpdateInvestigation(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsInvestigator]
    serializer_class = UpdateInvestigationSr
    lookup_field = "investigation_id"
    queryset = Investigation.objects.all()
