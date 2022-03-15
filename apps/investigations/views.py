import uuid
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.high_consumptions.models import HC
from apps.investigations.tasks import send_created_investigation
from core.models import Facility

from core.permissions import enforce_parameters
from .permissions import IsInvestigationManager, IsInvestigator, HasInvestigationAccess
from .serializers import (
    CreateInvestigationSr,
    UpdateInvestigationSr,
    GetInvestigationsSr,
    CreateInvestigationByHCSchema,
)
from .models import Investigation
from .filters import GetInvestigationsFl
from .paginations import GetInvestigationsPg
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile
from django.db.models import Q


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


class GetAssignedInvestigations(ListAPIView):
    permission_classes = [IsAuthenticated, HasInvestigationAccess]
    serializer_class = GetInvestigationsSr
    pagination_class = GetInvestigationsPg

    def get_queryset(self):
        return Investigation.objects.filter(
            Q(
                investigation_investigator=self.request.user.user_info,
                require_bas_fix=False,
            )
            | Q(investigation_tech=self.request.user.user_info, require_bas_fix=True),
            closed=False,
            in_approval=False,
        )


class GetInvestigations(ListAPIView):
    permission_classes = [IsAuthenticated, HasInvestigationAccess]
    serializer_class = GetInvestigationsSr
    queryset = (
        Investigation.objects.all()
        .select_related("investigation_investigator")
        .select_related("investigation_creator")
        .select_related("investigation_tech")
        .select_related("facility")
    )
    filterset_class = GetInvestigationsFl
    pagination_class = GetInvestigationsPg


@method_decorator(
    **{
        "name": "post",
        "decorator": swagger_auto_schema(
            request_body=CreateInvestigationByHCSchema,
            responses={200: "{'id': 'string'}"},
        ),
    }
)
class CreateInvestigationByHC(APIView):
    """
    Create investigations based on a created hc
    """

    permission_classes = [
        IsAuthenticated,
        IsInvestigationManager,
        HasInvestigationAccess,
    ]

    @method_decorator(
        enforce_parameters(
            params=[
                "hc_id",
                "facility",
                "investigation_date",
                "investigation_type",
                "investigation_description",
            ]
        )
    )
    def post(self, request):

        facility = Facility.objects.filter(facility_name=request.data["facility"])
        if not facility.exists():
            return Response(
                {"message": "Facility does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        facility = facility[0]

        hc = HC.objects.filter(
            hc_id=request.data["hc_id"],
            facility=facility,
            target_date=request.data["investigation_date"],
            utility_type=request.data["investigation_type"],
        )

        if not hc.exists():
            return Response(
                {"message": "HC does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )

        hc = hc[0]

        inv = Investigation.objects.filter(
            facility=facility,
            investigation_date=request.data["investigation_date"],
            investigation_type=request.data["investigation_type"],
        )

        # @NOTE: Avoid partial queries that will display only half of the data
        # When creating right away
        if not inv.exists():
            inv = Investigation(
                facility=facility,
                investigation_date=request.data["investigation_date"],
                investigation_type=request.data["investigation_type"],
            )
            inv.investigation_creator = request.user.user_info
            inv.investigation_metadata = {}
            inv.investigation_description = request.data["investigation_description"]
            inv.investigation_metadata["usage_increase"] = float(hc.usage_increase)
            inv.investigation_metadata["cost_increase"] = float(hc.cost_increase)

            if hc.hc_document:
                inv.investigation_document.save(
                    str(uuid.uuid4()) + ".html", ContentFile(hc.hc_document.read())
                )

            send_created_investigation(
                {
                    "facility": inv.facility,
                    "investigation_date": inv.investigation_date,
                    "investigation_type": inv.investigation_type,
                    "investigation_description": inv.investigation_description,
                }
            )

            inv.save()

        return Response(
            {
                "message": "Successfully Created Investigation",
                "id": inv.investigation_id,
            },
            status=status.HTTP_201_CREATED,
        )
