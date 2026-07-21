from rest_framework.test import APITestCase
from rest_framework import status

from team1.serializers import challenge
from .models.challenge import Challenge
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Activity, Challenge, Competition
class ChallengeCreateAPITest(APITestCase):
    def setUp(self):
  
        self.url = '/team1/api/challenges/' 
        
        # a valid payload for creating a challenge
        self.valid_payload = {
            "title": "test challenge",
            "description": "test challenge description",
            "difficulty": "easy",
            "activity_type": "running",
            "value_goal": "5.00",
            "goal_unit": "km",
            "date_start": "2026-07-21T00:00:00Z",
            "date_end": "2026-07-28T00:00:00Z",
        }

    def test_create_challenge_as_coach_success(self):
        """test: coach user can create a challenge"""
        headers = {
            'HTTP_X_USER_ROLE': 'coach',
            'HTTP_X_USER_ID': '123'

        }
        
        response = self.client.post(self.url, data=self.valid_payload, format='json', **headers)
        
        # check for 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # check that the challenge was created in the database
        challenge = Challenge.objects.get(title="test challenge")
        self.assertEqual(challenge.created_by, 123)

    def test_create_challenge_non_coach_forbidden(self):
        """test: non-coach user (e.g., student) gets 403 Forbidden"""
        headers = {
            'HTTP_X_USER_ROLE': 'student',
            'HTTP_X_USER_ID': '124'
        }
        
        response = self.client.post(self.url, data=self.valid_payload, format='json', **headers)
        
        # check for 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Challenge.objects.count(), 0)

    def test_create_challenge_missing_headers_forbidden(self):
        """test: sending request without authentication headers returns 403 Forbidden"""
        response = self.client.post(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_challenge_validation_error(self):
        """test: sending invalid data returns 400 Bad Request"""
        headers = {
            'HTTP_X_USER_ROLE': 'coach',
            'HTTP_X_USER_ID': '123'
        }
        # missing required fields (e.g., title is empty)
        invalid_payload = {
            "title": "",
            "description": "without title",
        }
        
        response = self.client.post(self.url, data=invalid_payload, format='json', **headers)
        
        # check for validation error (400 Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class ActivityCreateTests(APITestCase):
    """
    SCRUM-88: covers the happy path (successful submission) plus the
    validation errors introduced in SCRUM-85/86/87:
      - missing X-User-Id header
      - non-positive value
      - non-existent / deleted challenge
      - challenge that is not active (ended/cancelled)
      - activity_date outside the challenge's date_start/date_end window
    """

    def setUp(self):
        self.url = reverse('team1:activity-create')
        now = timezone.now()

        self.active_challenge = Challenge.objects.create(
            title="30-day running challenge",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=100,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now - timedelta(days=1),
            date_end=now + timedelta(days=29),
            status=Challenge.Status.ACTIVE,
            created_by=1,
        )

        self.ended_challenge = Challenge.objects.create(
            title="finished challenge",
            activity_type=Challenge.ActivityType.WALKING,
            difficulty=Challenge.Difficulty.EASY,
            value_goal=50,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now - timedelta(days=60),
            date_end=now - timedelta(days=30),
            status=Challenge.Status.ENDED,
            created_by=1,
        )

    def _post(self, data, user_id="42"):
        headers = {}
        if user_id is not None:
            headers['HTTP_X_USER_ID'] = user_id
        return self.client.post(self.url, data, format='json', **headers)

    # --- happy path ---

    def test_successful_submission(self):
        response = self._post({
            "challenge": self.active_challenge.challenge_id,
            "value": "5.50",
            "activity_date": timezone.now().date().isoformat(),
            "note": "morning run",
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activity.objects.count(), 1)

        activity = Activity.objects.first()
        self.assertEqual(activity.user_id, 42)
        self.assertEqual(activity.challenge_id, self.active_challenge.challenge_id)
        self.assertFalse(activity.is_deleted)

    # --- missing user header ---

    def test_missing_user_id_header_is_rejected(self):
        response = self._post(
            {
                "challenge": self.active_challenge.challenge_id,
                "value": "5",
                "activity_date": timezone.now().date().isoformat(),
            },
            user_id=None,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Activity.objects.count(), 0)

    # --- non-positive value ---

    def test_non_positive_value_is_rejected(self):
        response = self._post({
            "challenge": self.active_challenge.challenge_id,
            "value": "0",
            "activity_date": timezone.now().date().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("value", response.data)
        self.assertEqual(Activity.objects.count(), 0)

    # --- invalid / missing challenge ---

    def test_nonexistent_challenge_is_rejected(self):
        response = self._post({
            "challenge": 999999,
            "value": "5",
            "activity_date": timezone.now().date().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Activity.objects.count(), 0)

    def test_deleted_challenge_is_rejected(self):
        self.active_challenge.is_deleted = True
        self.active_challenge.save()

        response = self._post({
            "challenge": self.active_challenge.challenge_id,
            "value": "5",
            "activity_date": timezone.now().date().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("challenge", response.data)
        self.assertEqual(Activity.objects.count(), 0)

    # --- inactive (ended) challenge ---

    def test_ended_challenge_is_rejected(self):
        response = self._post({
            "challenge": self.ended_challenge.challenge_id,
            "value": "5",
            "activity_date": (timezone.now() - timedelta(days=40)).date().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("challenge", response.data)
        self.assertEqual(Activity.objects.count(), 0)

    # --- activity_date outside the challenge's window ---

    def test_activity_date_outside_challenge_window_is_rejected(self):
        response = self._post({
            "challenge": self.active_challenge.challenge_id,
            "value": "5",
            "activity_date": (timezone.now() + timedelta(days=100)).date().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("activity_date", response.data)
        self.assertEqual(Activity.objects.count(), 0)

class CompetitionCreateAPITest(APITestCase):
    """SCRUM-126: unit tests for Competition creation permissions and validation."""

    def setUp(self):
        self.url = "/team1/api/competitions/"

        self.valid_payload = {
            "title": "Summer Weight-Loss Cup",
            "description": "Weight loss competition among users",
            "rules": "Whoever loses the most weight (%) wins.",
            "competition_type": "weight_loss",
            "date_start": "2026-08-01T00:00:00Z",
            "date_end": "2026-08-31T23:59:59Z",
        }

    def _post(self, payload, role="coach", user_id="123"):
        headers = {"HTTP_X_USER_ROLE": role, "HTTP_X_USER_ID": user_id}
        return self.client.post(self.url, data=payload, format="json", **headers)

    def test_create_competition_as_coach_success(self):
        """A coach can create a competition; created_by comes from the header."""
        response = self._post(self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        competition = Competition.objects.get(title="Summer Weight-Loss Cup")
        self.assertEqual(competition.created_by, 123)
        self.assertEqual(competition.status, Competition.Status.PENDING)

    def test_create_competition_non_coach_forbidden(self):
        """A non-coach (e.g. a regular participant) gets 403 Forbidden."""
        response = self._post(self.valid_payload, role="student", user_id="124")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Competition.objects.count(), 0)

    def test_missing_user_id_header_is_rejected(self):
        headers = {"HTTP_X_USER_ROLE": "coach"}
        response = self.client.post(self.url, data=self.valid_payload, format="json", **headers)

        self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN))
        self.assertEqual(Competition.objects.count(), 0)

    def test_end_date_before_start_date_is_rejected(self):
        payload = dict(self.valid_payload)
        payload["date_start"] = "2026-08-31T00:00:00Z"
        payload["date_end"] = "2026-08-01T00:00:00Z"

        response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_end", response.data)
        self.assertEqual(Competition.objects.count(), 0)

    def test_invalid_competition_type_is_rejected(self):
        payload = dict(self.valid_payload)
        payload["competition_type"] = "not_a_real_type"

        response = self._post(payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Competition.objects.count(), 0)

class ActivityUpdateTests(APITestCase):
    """
    SCRUM-19:
    Tests updating an activity:
      - owner can edit on the same day
      - another user cannot edit the activity
      - editing an activity from a previous day is rejected
    """

    def setUp(self):
        self.url = lambda activity_id: reverse(
            "team1:activity-update",
            kwargs={"activity_id": activity_id},
        )

        now = timezone.now()

        self.challenge = Challenge.objects.create(
            title="Running Challenge",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=100,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now - timedelta(days=1),
            date_end=now + timedelta(days=10),
            status=Challenge.Status.ACTIVE,
            created_by=1,
        )

        self.today_activity = Activity.objects.create(
            user_id=42,
            challenge=self.challenge,
            value="5.00",
            activity_date=timezone.localdate(),
            note="Morning Run",
        )

        self.old_activity = Activity.objects.create(
            user_id=42,
            challenge=self.challenge,
            value="8.00",
            activity_date=timezone.localdate() - timedelta(days=1),
            note="Yesterday Run",
        )

    def _patch(self, activity_id, data, user_id="42"):
        headers = {}

        if user_id is not None:
            headers["HTTP_X_USER_ID"] = user_id

        return self.client.patch(
            self.url(activity_id),
            data=data,
            format="json",
            **headers
        )

    # ---------- happy path ----------

    def test_owner_can_update_activity_on_same_day(self):
        response = self._patch(
            self.today_activity.activity_id,
            {
                "challenge": self.challenge.challenge_id,
                "value": "10.50",
                "activity_date": timezone.localdate().isoformat(),
                "note": "Updated Run",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.today_activity.refresh_from_db()

        self.assertEqual(str(self.today_activity.value), "10.50")
        self.assertEqual(self.today_activity.note, "Updated Run")

    # ---------- wrong owner ----------

    def test_other_user_cannot_update_activity(self):
        response = self._patch(
            self.today_activity.activity_id,
            {
                "challenge": self.challenge.challenge_id,
                "value": "12",
                "activity_date": timezone.localdate().isoformat(),
            },
            user_id="999",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.today_activity.refresh_from_db()

        self.assertEqual(str(self.today_activity.value), "5.00")

    # ---------- previous day ----------

    def test_previous_day_activity_cannot_be_updated(self):
        response = self._patch(
            self.old_activity.activity_id,
            {
                "challenge": self.challenge.challenge_id,
                "value": "15",
                "activity_date": self.old_activity.activity_date.isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.old_activity.refresh_from_db()

        self.assertEqual(str(self.old_activity.value), "8.00")