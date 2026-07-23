"""
BUGFIX: nothing ever moved a Competition to 'finished' when its date_end
passed - it only ever changed status via the manual /start/ and /finish/
endpoints a coach clicks. There's no scheduler/cron in this project (same
as Challenge, which uses this same "check on next request" pattern
instead of a real background job), so we lazily check-and-close here,
called from any endpoint that touches a competition.
"""

from django.utils import timezone

from ..models import Competition


def close_if_expired(competition):
    """
    If `competition` is still ACTIVE but its date_end has passed, marks
    it FINISHED and returns True (caller can react, e.g. reject a result
    submission). Otherwise returns False. Safe/idempotent to call on
    every request.
    """
    if (
        competition.status == Competition.Status.ACTIVE
        and competition.date_end <= timezone.now()
    ):
        competition.status = Competition.Status.FINISHED
        competition.save(update_fields=["status"])
        return True

    return False