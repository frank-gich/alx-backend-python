import django_filters
from django.db.models import Q
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from .models import Message, Conversation

User = get_user_model()


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model with various filtering options.
    """
    # Time range filtering - CHANGE 'timestamp' to your actual field name
    start_date = django_filters.DateTimeFilter(
        field_name='created_at',  # Change this to match your model field
        lookup_expr='gte',
        help_text='Filter messages from this date/time onwards (YYYY-MM-DD HH:MM:SS)'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='created_at',  # Change this to match your model field
        lookup_expr='lte',
        help_text='Filter messages up to this date/time (YYYY-MM-DD HH:MM:SS)'
    )
    
    # Date only filtering (alternative to datetime)
    date_from = django_filters.DateFilter(
        field_name='created_at__date',  # Change this to match your model field
        lookup_expr='gte',
        help_text='Filter messages from this date onwards (YYYY-MM-DD)'
    )
    date_to = django_filters.DateFilter(
        field_name='created_at__date',  # Change this to match your model field
        lookup_expr='lte',
        help_text='Filter messages up to this date (YYYY-MM-DD)'
    )
    
    # Specific date filtering
    date = django_filters.DateFilter(
        field_name='created_at__date',  # Change this to match your model field
        help_text='Filter messages from a specific date (YYYY-MM-DD)'
    )
    
    # Conversation filtering
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        help_text='Filter messages by conversation ID'
    )
    
    # Sender filtering
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text='Filter messages by sender user ID'
    )
    
    # Sender username filtering
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text='Filter messages by sender username (case-insensitive)'
    )
    
    # Content search
    content = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Search messages by content (case-insensitive)'
    )
    
    # Search across multiple fields
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Search messages by content or sender username'
    )
    
    # Messages with specific users (participants)
    with_user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method='filter_with_user',
        help_text='Filter messages from conversations with specific user'
    )
    
    # Messages with specific users by username
    with_username = django_filters.CharFilter(
        method='filter_with_username',
        help_text='Filter messages from conversations with specific username'
    )
    
    # Time-based filtering options
    last_hour = django_filters.BooleanFilter(
        method='filter_last_hour',
        help_text='Filter messages from the last hour'
    )
    
    last_day = django_filters.BooleanFilter(
        method='filter_last_day',
        help_text='Filter messages from the last 24 hours'
    )
    
    last_week = django_filters.BooleanFilter(
        method='filter_last_week',
        help_text='Filter messages from the last 7 days'
    )
    
    # Ordering options
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),  # Change this to match your model field
            ('sender__username', 'sender'),
            ('conversation__id', 'conversation'),
        ),
        field_labels={
            'created_at': 'Date/Time',  # Change this to match your model field
            'sender__username': 'Sender',
            'conversation__id': 'Conversation',
        }
    )
    
    class Meta:
        model = Message
        fields = {
            'conversation': ['exact'],
            'sender': ['exact'],
            # Temporarily comment out datetime field until we confirm the actual field name
            # 'created_at': ['exact', 'gte', 'lte', 'year', 'month', 'day'],
        }
    
    def filter_search(self, queryset, name, value):
        """
        Search across message content and sender username.
        """
        if value:
            return queryset.filter(
                Q(message_body__icontains=value) |
                Q(sender__username__icontains=value) |
                Q(sender__first_name__icontains=value) |
                Q(sender__last_name__icontains=value)
            )
        return queryset
    
    def filter_with_user(self, queryset, name, value):
        """
        Filter messages from conversations that include a specific user.
        """
        if value:
            return queryset.filter(conversation__participants=value)
        return queryset
    
    def filter_with_username(self, queryset, name, value):
        """
        Filter messages from conversations that include a user with specific username.
        """
        if value:
            try:
                user = User.objects.get(username__icontains=value)
                return queryset.filter(conversation__participants=user)
            except User.DoesNotExist:
                return queryset.none()
        return queryset
    
    def filter_last_hour(self, queryset, name, value):
        """
        Filter messages from the last hour.
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            one_hour_ago = timezone.now() - timedelta(hours=1)
            return queryset.filter(created_at__gte=one_hour_ago)  # Change 'timestamp' to your actual field name
        return queryset
    
    def filter_last_day(self, queryset, name, value):
        """
        Filter messages from the last 24 hours.
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            one_day_ago = timezone.now() - timedelta(days=1)
            return queryset.filter(created_at__gte=one_day_ago)  # Change 'timestamp' to your actual field name
        return queryset
    
    def filter_last_week(self, queryset, name, value):
        """
        Filter messages from the last 7 days.
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            one_week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=one_week_ago)  # Change 'timestamp' to your actual field name
        return queryset


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model.
    """
    # Participants filtering
    with_user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        help_text='Filter conversations with specific user'
    )
    
    with_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text='Filter conversations with specific username'
    )
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this date/time'
    )
    
    # Updated filtering
    updated_after = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        help_text='Filter conversations updated after this date/time'
    )
    
    # Participant count filtering
    min_participants = django_filters.NumberFilter(
        method='filter_min_participants',
        help_text='Filter conversations with minimum number of participants'
    )
    
    max_participants = django_filters.NumberFilter(
        method='filter_max_participants',
        help_text='Filter conversations with maximum number of participants'
    )
    
    # Has messages filtering
    has_messages = django_filters.BooleanFilter(
        method='filter_has_messages',
        help_text='Filter conversations that have messages'
    )
    
    # Recent activity
    recent_activity = django_filters.BooleanFilter(
        method='filter_recent_activity',
        help_text='Filter conversations with recent activity (last 24 hours)'
    )
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created'),
            ('updated_at', 'updated'),
        ),
        field_labels={
            'created_at': 'Created Date',
            'updated_at': 'Last Updated',
        }
    )
    
    class Meta:
        model = Conversation
        fields = {
            # Only include fields that actually exist in your Conversation model
            # Remove or comment out fields that don't exist
            # 'created_at': ['exact', 'gte', 'lte'],
            # 'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_min_participants(self, queryset, name, value):
        """
        Filter conversations with minimum number of participants.
        """
        if value:
            from django.db import models
            return queryset.annotate(
                participant_count=models.Count('participants')
            ).filter(participant_count__gte=value)
        return queryset
    
    def filter_max_participants(self, queryset, name, value):
        """
        Filter conversations with maximum number of participants.
        """
        if value:
            from django.db import models
            return queryset.annotate(
                participant_count=models.Count('participants')
            ).filter(participant_count__lte=value)
        return queryset
    
    def filter_has_messages(self, queryset, name, value):
        """
        Filter conversations that have messages.
        """
        if value:
            return queryset.filter(messages__isnull=False).distinct()
        elif value is False:
            return queryset.filter(messages__isnull=True)
        return queryset
    
    def filter_recent_activity(self, queryset, name, value):
        """
        Filter conversations with recent activity.
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            one_day_ago = timezone.now() - timedelta(days=1)
            return queryset.filter(
                Q(messages__created_at__gte=one_day_ago) |  # Change 'timestamp' to your actual field name
                Q(updated_at__gte=one_day_ago)
            ).distinct()
        return queryset