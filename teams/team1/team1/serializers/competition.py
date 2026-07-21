from rest_framework import serializers

from ..models import Competition


class CompetitionSerializer(serializers.ModelSerializer):
    """SCRUM-123: CompetitionSerializer with field validation."""

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
        if data.get("date_start") and data.get("date_end"):
            if data["date_end"] <= data["date_start"]:
                raise serializers.ValidationError({
                    "date_end": "the end date (date_end) must be after the start date (date_start)."
                })

        title = data.get("title")
        if title is not None and not title.strip():
            raise serializers.ValidationError({
                "title": "title must not be empty."
            })

        return data