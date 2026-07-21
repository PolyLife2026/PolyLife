from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsCoach(BasePermission):
    """
    Custom permission to only allow users with the role of 'coach' to create challenges.
    """
    message = "You are not allowed to create challenges. Only coaches are permitted."

    def has_permission(self, request, view):    
        # Get the user role from the header
        role = request.headers.get('X-User-Role')
        
        # Check if the user role is 'coach'
        if role and role.lower() == 'coach':
            return True
            
        return False
    
class IsChallengeCreator(permissions.BasePermission):
    """
    Object-level permission to only allow the creator of a challenge to edit it.
    """
    message = "You do not have permission to edit this challenge. Only the creator can edit it."

    def has_object_permission(self, request, view, obj):
        # Read the user ID from the microservice header
        user_id = request.headers.get('X-User-Id')
        
        # Compare header user_id with the challenge's created_by field
        # Note: We convert both to string to ensure safe comparison
        if not user_id:
            return False
            
        # Assuming obj.created_by stores the user ID as an integer or string
        return str(obj.created_by) == str(user_id)
