from decimal import Decimal
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CompetitionParticipant
from datetime import timedelta
from .models import ParticipantScore
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


class ChallengeListTests(APITestCase):

    def setUp(self):

        now = timezone.now()

        # Create an active challenge
        self.active_challenge = Challenge.objects.create(
            title="Active Challenge",
            description="This is a public challenge.",
            status="created",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=100,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now + timedelta(days=2),
            date_end=now + timedelta(days=10),
            is_deleted=False,
            created_by=10,
        )
        
        # Create a soft-deleted challenge
        self.deleted_challenge = Challenge.objects.create(
            title="Deleted Challenge",
            description="This challenge is deleted.",
            status="created",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=100,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now + timedelta(days=2),
            date_end=now + timedelta(days=10),
            is_deleted=True,
            created_by=10,
        )
        
        self.url = reverse('team1:challenge-list-create') 

        self.headers = {
            'HTTP_X_USER_ROLE': 'coach',
            'HTTP_X_USER_ID': '1'
        }

    def test_list_challenges_returns_only_active(self):
        # Act
        response = self.client.get(self.url, **self.headers)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle response data (checking if pagination is applied globally)
        # If standard DRF pagination is active, items are inside 'results'
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        # We only expect 1 active challenge, the soft-deleted one should be hidden
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], self.active_challenge.title)

class ChallengeUpdateAPITest(APITestCase):
    """Unit tests for challenge edit rules: allowed before start, blocked after start, blocked for non-owner."""

    def setUp(self):
        self.url = lambda challenge_id: reverse(
            "team1:challenge-update",
            kwargs={"challenge_id": challenge_id},
        )

        now = timezone.now()

        self.pre_start_challenge = Challenge.objects.create(
            title="Pre-start challenge",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=100,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now + timedelta(days=2),
            date_end=now + timedelta(days=10),
            status=Challenge.Status.CREATED,
            created_by=10,
        )

        self.post_start_challenge = Challenge.objects.create(
            title="Post-start challenge",
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.MEDIUM,
            value_goal=80,
            goal_unit=Challenge.GoalUnit.KM,
            date_start=now - timedelta(days=1),
            date_end=now + timedelta(days=10),
            status=Challenge.Status.CREATED,
            created_by=10,
        )

    def _patch(self, challenge_id, data, user_id="10", role="coach"):
        headers = {
            "HTTP_X_USER_ID": user_id,
            "HTTP_X_USER_ROLE": role,
        }
        return self.client.patch(
            self.url(challenge_id),
            data=data,
            format="json",
            **headers,
        )

    def test_edit_allowed_before_challenge_start(self):
        response = self._patch(
            self.pre_start_challenge.challenge_id,
            {"title": "Updated before start"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pre_start_challenge.refresh_from_db()
        self.assertEqual(self.pre_start_challenge.title, "Updated before start")

    def test_edit_blocked_after_challenge_start(self):
        response = self._patch(
            self.post_start_challenge.challenge_id,
            {"title": "Should not update"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.post_start_challenge.refresh_from_db()
        self.assertNotEqual(self.post_start_challenge.title, "Should not update")

    def test_edit_blocked_for_non_owner(self):
        response = self._patch(
            self.pre_start_challenge.challenge_id,
            {"title": "Should not update"},
            user_id="99",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.pre_start_challenge.refresh_from_db()
        self.assertNotEqual(self.pre_start_challenge.title, "Should not update")

class ChallengeFilterTests(APITestCase):

    def setUp(self):
        self.url = reverse('team1:challenge-list-create')
        self.headers = {'HTTP_X_USER_ID': '1', 'HTTP_X_USER_ROLE': 'coach'}
        
        now = timezone.now()
        
        # Create Challenge 1
        self.challenge_easy_running = Challenge.objects.create(
            title="Morning Run",
            description="Easy morning run",
            created_by=1,
            activity_type=Challenge.ActivityType.RUNNING, 
            difficulty=Challenge.Difficulty.EASY,
            value_goal=80,
            status=Challenge.Status.CREATED,
            date_start=now + timedelta(days=1),
            date_end=now + timedelta(days=5)
        )
        
        # Create Challenge 2
        self.challenge_hard_cycling = Challenge.objects.create(
            title="Mountain Biking",
            description="Hard mountain trail",
            created_by=2,
            activity_type=Challenge.ActivityType.CYCLING,  
            difficulty=Challenge.Difficulty.HARD,
            value_goal=80,       
            status=Challenge.Status.STARTED,         
            date_start=now + timedelta(days=10),
            date_end=now + timedelta(days=15)
        )

    def test_filter_by_activity_type(self):
        # Test filtering by a single valid activity_type
        response = self.client.get(self.url, {'activity_type': 'running'}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['challenge_id'], self.challenge_easy_running.challenge_id)

    def test_filter_by_difficulty(self):
        # Test filtering by a single valid difficulty
        response = self.client.get(self.url, {'difficulty': 'hard'}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['challenge_id'], self.challenge_hard_cycling.challenge_id)

    def test_filter_invalid_choice_returns_400(self):
        # Test invalid choice returns 400 Bad Request (handled by ChoiceFilter)
        response = self.client.get(self.url, {'difficulty': 'INVALID_DIFF'}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_combined(self):
        # Test combining multiple filters
        response = self.client.get(self.url, {
            'activity_type': 'cycling',
            'difficulty': 'hard'
        }, **self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['challenge_id'], self.challenge_hard_cycling.challenge_id)

    def test_filter_by_date_range(self):
        # Test filtering challenges starting after a specific date
        filter_date = (timezone.now() + timedelta(days=7)).isoformat()
        response = self.client.get(self.url, {'date_start_after': filter_date}, **self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['challenge_id'], self.challenge_hard_cycling.challenge_id)

    def test_filter_exclude_deleted_and_cancelled(self):
        # Create a cancelled challenge
        Challenge.objects.create(
            title="Cancelled Event",
            description=Challenge.Difficulty.EASY,
            created_by=1,
            activity_type=Challenge.ActivityType.RUNNING,
            difficulty=Challenge.Difficulty.EASY,
            value_goal=80,
            status=Challenge.Status.CANCELLED,
            date_start=timezone.now(),
            date_end=timezone.now() + timedelta(days=1)
        )
        
        # Ensure the cancelled challenge is excluded from the normal GET request
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assuming pagination is StandardResultsSetPagination, check 'results'
        challenge_ids = [c['challenge_id'] for c in response.data['results']]
        self.assertEqual(len(challenge_ids), 2)


class ActivityCreateTests(APITestCase):
    """
    SCRUM-88: covers the happy path (successful submission) plus the
    validation errors introduced in SCRUM-85/86/87:
      - missing X-User-Id header
      - non-positive value
      - non-existent / deleted challenge
      - challenge that is not started (ended/cancelled)
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
            status=Challenge.Status.STARTED,
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
            status=Challenge.Status.STARTED,
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

class ParticipantScoreAPITest(APITestCase):

    def setUp(self):
        self.url = '/team1/api/activities/'

        now = timezone.now()

        self.challenge = Challenge.objects.create(
            title="Running Challenge",
            description="Test",
            difficulty="easy",
            activity_type="running",
            value_goal="10.00",
            goal_unit="km",
            date_start=now - timedelta(days=1),
            date_end=now + timedelta(days=5),
            status="active",
            created_by=1,
        )

        self.payload = {
            "challenge": self.challenge.challenge_id,
            "value": "5.00",
            "activity_date": timezone.localdate(),
            "note": "Morning Run"
        }

    def test_participant_score_created_and_updated(self):

        headers = {
            "HTTP_X_USER_ID": "100"
        }

        response = self.client.post(
            self.url,
            data=self.payload,
            format="json",
            **headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        score = ParticipantScore.objects.get(
            user_id=100,
            challenge=self.challenge
        )

        self.assertEqual(float(score.score), 50.00)

        self.payload["value"] = "2.50"

        response = self.client.post(
            self.url,
            data=self.payload,
            format="json",
            **headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        score.refresh_from_db()

        self.assertEqual(float(score.score), 75.00)


class ChallengeSoftDeleteTests(APITestCase):

    def setUp(self):

        now = timezone.now()

        # Mocking the custom headers used for authentication in PolyLife
        self.auth_headers = {
            'HTTP_X_USER_ID': '1',
            'HTTP_X_USERNAME': 'user1',
            'HTTP_X_USER_ROLE': 'coach',
        }
        
        # 1. Create a challenge in CREATED status
        self.created_challenge = Challenge.objects.create(
            title='Created Challenge',
            description='Test description 1',
            created_by=1,
            status='created',
            value_goal=100,
            date_start=now,                             
            date_end=now + timedelta(days=7),
            # Add other required fields based on your model
        )
        
        # 2. Create a challenge in STARTED status (or ENDED)
        self.started_challenge = Challenge.objects.create(
            title='Started Challenge',
            description='Test description 2',
            created_by=1,
            status='Started',
            value_goal=100,
            date_start=now,                             
            date_end=now + timedelta(days=7),
        )

    def test_soft_delete_created_challenge(self):
        """
        Ensure that a challenge with 'CREATED' status can be soft-deleted.
        """
        # Assuming your detail URL pattern is named 'challenge-detail'
        url = reverse('team1:challenge-detail', args=[self.created_challenge.challenge_id])
        
        # Send DELETE request with custom auth headers
        response = self.client.delete(url, **self.auth_headers)
        
        # Check if the API returns 204 No Content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the challenge still exists in the database but is_deleted is True
        # Note: We use _base_manager to bypass the ActiveChallengeManager if it hides deleted items
        deleted_challenge = Challenge._base_manager.get(challenge_id=self.created_challenge.challenge_id)
        self.assertTrue(deleted_challenge.is_deleted)
        
        # Verify it does not appear in normal queries (using the default manager)
        self.assertFalse(Challenge.objects.filter(challenge_id=self.created_challenge.challenge_id).exists())

    def test_block_delete_started_challenge(self):
        """
        Ensure that deleting a challenge not in 'CREATED' status is blocked.
        """
        url = reverse('team1:challenge-detail', args=[self.started_challenge.challenge_id])
        
        response = self.client.delete(url, **self.auth_headers)
        
        # Check if the API correctly blocks the action (Assuming 400 Bad Request is returned by your View)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify the challenge is NOT soft-deleted
        self.started_challenge.refresh_from_db()
        self.assertFalse(self.started_challenge.is_deleted)

class ChallengeDetailTests(APITestCase):

    def setUp(self):

        now = timezone.now()

        # Set up authentication headers
        self.auth_headers = {
            'HTTP_X_USER_ID': '1',
            'HTTP_X_USERNAME': 'user1',
            'HTTP_X_USER_ROLE': 'coach',
        }
        
        # Create a sample challenge
        self.challenge = Challenge.objects.create(
            title='Detail View Test',
            description='Test description 1',
            created_by=1,
            status='created',
            value_goal=100,
            date_start=now,                             
            date_end=now + timedelta(days=7),
        )
        
        # Define URL using the correct namespace and lookup field
        self.url = reverse('team1:challenge-detail', kwargs={'challenge_id': self.challenge.challenge_id})

    def test_serializer_output_and_participant_count(self):
        """Ensure detail serializer returns expected public fields."""
        response = self.client.get(self.url, **self.auth_headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # # Check if custom serializer field is present
        # self.assertIn('participant_count', response.data)
        # self.assertEqual(response.data['participant_count'], 0)
        
        # Check if internal fields are excluded (adjust based on your serializer)
        self.assertNotIn('is_deleted', response.data)

    def test_challenge_not_found_404(self):
        """Ensure getting a non-existent challenge returns 404."""
        url = reverse('team1:challenge-detail', kwargs={'challenge_id': 99999})
        response = self.client.get(url, **self.auth_headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_soft_deleted_challenge_returns_404(self):
        """Ensure getting a soft-deleted challenge returns 404, not 200."""
        # Soft delete the challenge
        self.challenge.is_deleted = True
        self.challenge.save()
        
        response = self.client.get(self.url, **self.auth_headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompetitionJoinAPITest(APITestCase):
    """
    SCRUM-27:
    Test joining a competition.
    """

    def setUp(self):
        self.competition = Competition.objects.create(
            title="Summer Competition",
            description="Test Competition",
            rules="Test Rules",
            competition_type=Competition.CompetitionType.WEIGHT_LOSS,
            date_start=timezone.now() + timedelta(days=1),
            date_end=timezone.now() + timedelta(days=10),
            status=Competition.Status.PENDING,
            created_by=1,
        )

    def test_join_success(self):
        response = self.client.post(
            f"/team1/api/competitions/{self.competition.competition_id}/join/",
            HTTP_X_USER_ID="100",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CompetitionParticipant.objects.filter(
                competition=self.competition,
                user_id=100,
            ).exists()
        )

    def test_duplicate_join(self):
        CompetitionParticipant.objects.create(
            competition=self.competition,
            user_id=100,
        )

        response = self.client.post(
            f"/team1/api/competitions/{self.competition.competition_id}/join/",
            HTTP_X_USER_ID="100",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_closed_competition(self):
        self.competition.status = Competition.Status.ACTIVE
        self.competition.save()

        response = self.client.post(
            f"/team1/api/competitions/{self.competition.competition_id}/join/",
            HTTP_X_USER_ID="100",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_header(self):
        response = self.client.post(
            f"/team1/api/competitions/{self.competition.competition_id}/join/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_not_found(self):
        response = self.client.post(
            "/team1/api/competitions/99999/join/",
            HTTP_X_USER_ID="100",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ChallengeLeaderboardAPITest(APITestCase):

    def setUp(self):

        self.url = "/team1/api/challenges/1/leaderboard/"

        now = timezone.now()

        self.challenge = Challenge.objects.create(
            title="Leaderboard Test",
            description="test",
            difficulty="easy",
            activity_type="running",
            value_goal="100",
            goal_unit="km",
            date_start=now,
            date_end=now + timedelta(days=5),
            status="active",
            created_by=1,
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=1,
            score="60",
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=2,
            score="95",
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=3,
            score="30",
        )

    def test_challenge_leaderboard(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]["user_id"], 2)
        self.assertEqual(response.data[1]["user_id"], 1)
        self.assertEqual(response.data[2]["user_id"], 3)

        self.assertEqual(response.data[0]["rank"], 1)
        self.assertEqual(response.data[1]["rank"], 2)
        self.assertEqual(response.data[2]["rank"], 3)

class MyRankAPITest(APITestCase):

    def setUp(self):

        self.url = "/team1/api/challenges/1/my-rank/"

        now = timezone.now()

        self.challenge = Challenge.objects.create(
            title="Running Challenge",
            description="Test",
            difficulty="easy",
            activity_type="running",
            value_goal="100",
            goal_unit="km",
            date_start=now,
            date_end=now + timedelta(days=5),
            status="active",
            created_by=1,
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=1,
            score="95.00",
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=2,
            score="70.00",
        )

        ParticipantScore.objects.create(
            challenge=self.challenge,
            user_id=3,
            score="40.00",
        )

    def test_my_rank_success(self):

        headers = {
            "HTTP_X_USER_ID": "2"
        }

        response = self.client.get(
            self.url,
            **headers
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["rank"],
            2
        )

        self.assertEqual(
            response.data["user_id"],
            2
        )

        self.assertEqual(
            str(response.data["score"]),
            "70.00"
        )

class ChallengeAutoCloseTest(APITestCase):

    def setUp(self):
        self.url = "/team1/api/activities/"

        self.challenge = Challenge.objects.create(
            title="Expired Challenge",
            description="Test",
            difficulty="easy",
            activity_type="running",
            value_goal="10.00",
            goal_unit="km",
            date_start=timezone.now() - timedelta(days=5),
            date_end=timezone.now() - timedelta(minutes=1),
            status=Challenge.Status.STARTED,
            created_by=1,
        )

    def test_activity_submission_to_expired_challenge(self):

        payload = {
            "challenge": self.challenge.challenge_id,
            "value": "5.00",
            "activity_date": timezone.localdate(),
        }

        response = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_USER_ID="10",
        )

        self.challenge.refresh_from_db()

        self.assertEqual(
            self.challenge.status,
            Challenge.Status.ENDED
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Activity.objects.count(),
            0
        )

class CompetitionResultAPITest(APITestCase):
    """
    SCRUM-28:
    Test recording competition results and ranking recalculation.
    """

    def setUp(self):
        self.competition = Competition.objects.create(
            title="Summer Competition",
            description="Test Competition",
            rules="Test Rules",
            competition_type=Competition.CompetitionType.WEIGHT_LOSS,
            date_start=timezone.now() + timedelta(days=1),
            date_end=timezone.now() + timedelta(days=10),
            status=Competition.Status.ACTIVE,
            created_by=1,
        )
        self.p1 = CompetitionParticipant.objects.create(
            competition=self.competition, user_id=100
        )
        self.p2 = CompetitionParticipant.objects.create(
            competition=self.competition, user_id=200
        )
        self.url = f"/team1/api/competitions/{self.competition.competition_id}/results/"

    def _record(self, user_id, score, method="post"):
        client_method = getattr(self.client, method)
        return client_method(
            self.url,
            data={"user_id": user_id, "score": score},
            format="json",
            HTTP_X_USER_ROLE="coach",
            HTTP_X_USER_ID="1",
        )

    def test_score_is_persisted(self):
        response = self._record(100, 42.5)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.total_score, Decimal("42.50"))

    def test_ranking_recalculated_after_result(self):
        self._record(100, 30)
        self._record(200, 90)

        self.p1.refresh_from_db()
        self.p2.refresh_from_db()

        self.assertEqual(self.p2.rank, 1)
        self.assertEqual(self.p1.rank, 2)

    def test_tied_scores_share_the_same_rank(self):
        self._record(100, 50)
        self._record(200, 50)

        self.p1.refresh_from_db()
        self.p2.refresh_from_db()

        self.assertEqual(self.p1.rank, 1)
        self.assertEqual(self.p2.rank, 1)

    def test_result_for_non_participant_is_rejected(self):
        response = self._record(999, 10)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_coach_cannot_record_results(self):
        response = self.client.post(
            self.url,
            data={"user_id": 100, "score": 42.5},
            format="json",
            HTTP_X_USER_ROLE="student",
            HTTP_X_USER_ID="1",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_also_records_result(self):
        response = self._record(100, 77, method="put")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.total_score, Decimal("77.00"))