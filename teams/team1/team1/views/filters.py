import django_filters
from ..models import Challenge

class ChallengeFilter(django_filters.FilterSet):

    activity_type = django_filters.CharFilter(field_name='activity_type', lookup_expr='iexact')
    difficulty = django_filters.CharFilter(field_name='difficulty', lookup_expr='iexact')
    
    # Filtering based on date range since 'duration' is not a direct DB field
    date_start_after = django_filters.DateTimeFilter(field_name='date_start', lookup_expr='gte')
    date_end_before = django_filters.DateTimeFilter(field_name='date_end', lookup_expr='lte')

    class Meta:
        model = Challenge
        fields = ['activity_type', 'difficulty', 'date_start_after', 'date_end_before']
