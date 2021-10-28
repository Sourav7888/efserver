from rest_framework import serializers
from .models import Investigation


class GetInvestigationsSr(serializers.ModelSerializer):
    class Meta:
        model = Investigation
        fields = "__all__"


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
    def check_context(self, instance, context):
        """
        Check and assign an investigator if no one is assigned to
        the investigation
        """
        request = context["request"]
        investigator = instance.investigation_investigator_id
        user = request.user.user_info

        if investigator is None:
            instance.investigation_investigator_id = user
            instance.save()
            return True

        elif investigator == user.user_unique_id:
            return True

        return False

    def update(self, instance, validated_data):
        # can only update if the current user is the investigator of
        # the investigation
        if self.check_context(instance, self.context):
            return super().update(instance, validated_data)

        raise serializers.ValidationError(
            {"message": "You are not allowed to perform this action!"}
        )

    def partial_update(self, instance, validated_data):
        """
        When asking for a patch only the investigator gets updated
        """
        # can only update if the current user is the investigator of
        # the investigation
        if self.check_context(instance, self.context):
            return super().partial_update(instance, validated_data)

        raise serializers.ValidationError(
            {"message": "You are not allowed to perform this action!"}
        )

    class Meta:
        model = Investigation
        fields = [
            "investigation_result",
            "in_approval",
            "closed",
        ]
