from rest_framework import serializers
from .models import Investigation


class CreateInvestigationSr(serializers.ModelSerializer):
    def create(self, validated_data):
        investigation = Investigation.objects.create(**validated_data)
        setattr(
            investigation,
            "investigation_creator_id",
            self.context["request"].user.user_info,
        )

        investigation.save()

        return investigation

    class Meta:
        model = Investigation
        fields = [
            "investigation_id",
            "facility",
            "investigation_date",
            "investigation_type",
            "investigation_description",
        ]


class UpdateInvestigationSr(serializers.ModelSerializer):
    class Meta:
        model = Investigation
        fields = [
            "investigation_investigator",
            "investigation_description",
            "in_approval",
            "closed",
        ]
