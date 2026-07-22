from rest_framework import serializers

from ..models import Competition, CompetitionParticipant


class CompetitionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            "competition_id",
            "title",
            "status",
            "competition_type",
            "date_start",
            "date_end",
        ]


class CompetitionDetailSerializer(serializers.ModelSerializer):
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = [
            "competition_id",
            "title",
            "description",
            "rules",
            "competition_type",
            "date_start",
            "date_end",
            "status",
            "created_by",
            "is_joined",
        ]
        read_only_fields = fields

    def get_is_joined(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user_id = request.META.get("HTTP_X_USER_ID")
        if not user_id:
            return False
        return CompetitionParticipant.objects.filter(
            competition=obj,
            user_id=int(user_id),
        ).exists()


class CompetitionSerializer(serializers.ModelSerializer):
    """
    SCRUM-123: CompetitionSerializer with field validation.
    """

    class Meta:
        model = Competition
        fields = "__all__"
        read_only_fields = (
            "competition_id",
            "created_at",
            "updated_at",
            "is_deleted",
            "created_by",
        )

    def validate(self, data):
        """
        Validate competition dates and title.
        """

        date_start = data.get("date_start")
        date_end = data.get("date_end")

        if date_start and date_end and date_end <= date_start:
            raise serializers.ValidationError({
                "date_end": (
                    "The end date (date_end) must be after the start date."
                )
            })

        title = data.get("title")

        if title is not None and not title.strip():
            raise serializers.ValidationError({
                "title": "Title must not be empty."
            })

        return data