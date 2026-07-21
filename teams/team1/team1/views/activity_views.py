from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import Activity, Challenge
from ..serializers.activity import ActivitySerializer


class ActivityCreateView(generics.CreateAPIView):
    """
    POST /team1/api/activities/
    Lets a logged-in participant submit a daily activity for a challenge.
    The request body should contain challenge, value, activity_date and
    (optionally) note in JSON format. user_id is NOT read from the body —
    it is taken from the X-User-Id header set by the Gateway.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    authentication_classes = []
    permission_classes = []

    def perform_create(self, serializer):
        # Get the user id from the request headers.
        user_id = self.request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers.")

        challenge = serializer.validated_data["challenge"]

        # Automatically close challenge if it has expired
        if (
                challenge.status == Challenge.Status.STARTED
                and challenge.date_end <= timezone.now()
        ):
            challenge.status = Challenge.Status.ENDED
            challenge.save(update_fields=["status"])

            raise ValidationError({
                "challenge": "This challenge has ended and no longer accepts activities."
            })

        serializer.save(user_id=user_id)


class ActivityUpdateView(generics.UpdateAPIView):
    queryset = Activity.objects.filter(is_deleted=False)
    serializer_class = ActivitySerializer

    authentication_classes = []
    permission_classes = []

    lookup_field = "activity_id"

    def perform_update(self, serializer):
        user_id = self.request.META.get("HTTP_X_USER_ID")

        if not user_id:
            raise PermissionDenied("Missing user id in headers.")

        activity = self.get_object()

        # Only the owner can edit the activity
        if str(activity.user_id) != str(user_id):
            raise PermissionDenied(
                "You can only edit your own activities."
            )

        challenge = activity.challenge

        # Automatically close challenge if it has expired
        if (
                challenge.status == Challenge.Status.STARTED
                and challenge.date_end <= timezone.now()
        ):
            challenge.status = Challenge.Status.ENDED
            challenge.save(update_fields=["status"])

            raise ValidationError({
                "challenge": "This challenge has ended and activities can no longer be edited."
            })

        # Only allow editing on the same day
        today = timezone.localdate()

        if activity.activity_date != today:
            raise ValidationError({
                "activity_date":
                    "Activities can only be edited on the same day."
            })

        serializer.save()