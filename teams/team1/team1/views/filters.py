import django_filters
from ..models import Challenge

class ChallengeFilter(django_filters.FilterSet):
    '''
    FilterSet for the Challenge model, allowing filtering by activity type, difficulty, and date range.
    '''

    activity_type = django_filters.ChoiceFilter(
        choices=Challenge.ActivityType.choices,
        help_text="Filter by exact activity type."
    )
    
    difficulty = django_filters.ChoiceFilter(
        choices=Challenge.Difficulty.choices,
        help_text="Filter by exact difficulty level."
    )
    
    # Filtering based on date range since 'duration' is not a direct DB field
    date_start_after = django_filters.DateTimeFilter(field_name='date_start', lookup_expr='gte')
    date_end_before = django_filters.DateTimeFilter(field_name='date_end', lookup_expr='lte')

    class Meta:
        model = Challenge
        fields = ['activity_type', 'difficulty', 'date_start_after', 'date_end_before']
