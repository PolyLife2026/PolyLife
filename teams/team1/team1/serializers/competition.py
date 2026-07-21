from rest_framework import serializers

from ..models import Competition


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