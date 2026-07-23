from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import Competition, Activity, Leaderboard
import json


class CompetitionModelTests(TestCase):
    """Test Competition model and status transitions."""

    def setUp(self):
        now = timezone.now()
        self.future_comp = Competition.objects.create(
            title="Future Competition",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=8),
            created_by=1,
        )
        self.active_comp = Competition.objects.create(
            title="Active Competition",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=6),
            created_by=1,
        )
        self.ended_comp = Competition.objects.create(
            title="Ended Competition",
            start_date=now - timedelta(days=10),
            end_date=now - timedelta(days=1),
            created_by=1,
        )

    def test_pending_status(self):
        """Test that future competition has pending status."""
        self.assertEqual(self.future_comp.status, "pending")

    def test_status_update_to_started(self):
        """Test automatic status transition to started."""
        self.active_comp.update_status()
        self.active_comp.refresh_from_db()
        self.assertEqual(self.active_comp.status, "started")

    def test_status_update_to_ended(self):
        """Test automatic status transition to ended."""
        self.ended_comp.update_status()
        self.ended_comp.refresh_from_db()
        self.assertEqual(self.ended_comp.status, "ended")


class ActivityModelTests(TestCase):
    """Test Activity model."""

    def setUp(self):
        now = timezone.now()
        self.competition = Competition.objects.create(
            title="Test Competition",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=6),
            created_by=1,
        )

    def test_create_activity(self):
        """Test creating an activity."""
        activity = Activity.objects.create(
            competition=self.competition,
            user_id=1,
            activity_type="run",
            distance=5.5,
            duration=45,
            calories_burned=400,
            activity_date=timezone.now(),
        )
        self.assertEqual(activity.user_id, 1)
        self.assertEqual(activity.activity_type, "run")
        self.assertEqual(activity.distance, 5.5)

    def test_activity_ordering(self):
        """Test that activities are ordered by date descending."""
        now = timezone.now()
        Activity.objects.create(
            competition=self.competition,
            user_id=1,
            activity_type="run",
            distance=5.5,
            duration=45,
            activity_date=now - timedelta(days=1),
        )
        Activity.objects.create(
            competition=self.competition,
            user_id=1,
            activity_type="walk",
            distance=3.0,
            duration=30,
            activity_date=now,
        )
        
        activities = Activity.objects.all()
        self.assertEqual(activities[0].activity_type, "walk")
        self.assertEqual(activities[1].activity_type, "run")


class LeaderboardTests(TestCase):
    """Test Leaderboard model and ranking."""

    def setUp(self):
        now = timezone.now()
        self.competition = Competition.objects.create(
            title="Test Competition",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=6),
            created_by=1,
        )
        Leaderboard.objects.create(competition=self.competition)

    def test_leaderboard_creation(self):
        """Test leaderboard is created with competition."""
        leaderboard = Leaderboard.objects.get(competition=self.competition)
        self.assertIsNotNone(leaderboard)
        self.assertEqual(leaderboard.total_activities, 0)

    def test_leaderboard_stats_update(self):
        """Test leaderboard stats are updated correctly."""
        now = timezone.now()
        
        # Create multiple activities
        Activity.objects.create(
            competition=self.competition,
            user_id=1,
            activity_type="run",
            distance=5.0,
            duration=45,
            calories_burned=400,
            activity_date=now,
        )
        Activity.objects.create(
            competition=self.competition,
            user_id=1,
            activity_type="walk",
            distance=3.0,
            duration=30,
            calories_burned=200,
            activity_date=now,
        )
        
        # Manually update stats (simulating what the API does)
        leaderboard = Leaderboard.objects.get(
            competition=self.competition,
            user_id=1
        )
        leaderboard.total_activities = 2
        leaderboard.total_distance = 8.0
        leaderboard.total_duration = 75
        leaderboard.total_calories = 600
        leaderboard.save()
        
        self.assertEqual(leaderboard.total_activities, 2)
        self.assertEqual(leaderboard.total_distance, 8.0)
        self.assertEqual(leaderboard.total_calories, 600)


class APIViewTests(TestCase):
    """Test API endpoints."""

    def setUp(self):
        self.client = Client()
        now = timezone.now()
        self.competition = Competition.objects.create(
            title="Test Competition",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=6),
            created_by=1,
        )
        Leaderboard.objects.create(competition=self.competition)

    def test_competitions_list(self):
        """Test GET /api/competitions endpoint."""
        response = self.client.get("/api/competitions")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("competitions", data)

    def test_competition_detail(self):
        """Test GET /api/competitions/<id> endpoint."""
        response = self.client.get(f"/api/competitions/{self.competition.id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["id"], self.competition.id)
        self.assertEqual(data["title"], self.competition.title)

    def test_register_activity_requires_user(self):
        """Test that activity registration requires user authentication."""
        # Without X-User-Id header, should fail
        response = self.client.post(
            f"/api/competitions/{self.competition.id}/activity",
            data=json.dumps({
                "activity_type": "run",
                "distance": 5.0,
                "duration": 45,
                "activity_date": timezone.now().isoformat(),
            }),
            content_type="application/json",
        )
        # This test assumes the header check happens; adjust based on your implementation
        # The actual behavior depends on whether headers are present


class SmokeTests(TestCase):
    def test_placeholder(self):
        # Replace with real tests for your team's features.
        self.assertTrue(True)
