from rest_framework.permissions import BasePermission

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
