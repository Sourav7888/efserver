from .models import HC, HCReportTracker
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from apps.investigations.models import Investigation


class HCSr(ModelSerializer):
    investigation = serializers.SerializerMethodField()

    def get_investigation(self, obj):
        query = Investigation.objects.filter(
            facility=obj.facility,
            investigation_date=obj.target_date,
            investigation_type=obj.utility_type,
        )
        return (
            {"exists": False}
            if not query.exists()
            else {"exists": True, "id": query[0].investigation_id}
        )

    class Meta:
        model = HC
        fields = "__all__"


class HCReportTrackerSr(ModelSerializer):
    class Meta:
        model = HCReportTracker
        fields = "__all__"


class GenerateHCByDivisionSchema(serializers.Serializer):
    utility_type = serializers.CharField(max_length=100)
    division = serializers.CharField(max_length=100)
    investigation_date = serializers.DateField()


class DeleteGeneratedHCSchema(serializers.Serializer):

    hc_id = serializers.CharField()
