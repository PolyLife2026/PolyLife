from django.db import models
from ..models import Challenge

class ParticipantChallenge(models.Model):
    challenge = models.ForeignKey(
        'Challenge', 
        on_delete=models.CASCADE, 
        related_name='participants'
    )
    user_id = models.IntegerField(db_index=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    progress_current = models.PositiveIntegerField(default=0)
    score_total = models.IntegerField(default=0)
    
    # Nullable because it is calculated by the system later
    rank = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'participant_challenge'
        constraints = [
            models.UniqueConstraint(
                fields=['challenge', 'user_id'],
                name='unique_challenge_user'
            )
        ]

    def __str__(self):
        return f"User {self.user_id} - Challenge {self.challenge_id}"