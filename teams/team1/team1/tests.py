from rest_framework.test import APITestCase
from rest_framework import status

from team1.serializers import challenge
from .models.challenge import Challenge 

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

