"""
Serializers for the chats app models.
"""

from rest_framework import serializers
from .models import CustomUser, Conversation, Message


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information serializer."""
    
    class Meta:
        model = CustomUser
        fields = ('user_id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('user_id',)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for message model."""
    
    sender = UserBasicSerializer(read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = (
            'message_id', 'sender', 'sender_username', 'conversation', 
            'message_body', 'sent_at', 'created_at'
        )
        read_only_fields = ('message_id', 'sender', 'sent_at', 'created_at')


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    class Meta:
        model = Message
        fields = ('message_body',)
    
    def validate_message_body(self, value):
        """Validate message body is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """Basic conversation serializer."""
    
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_usernames = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of usernames to add as participants"
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participant_count = serializers.IntegerField(
        source='participants.count', 
        read_only=True
    )
    
    class Meta:
        model = Conversation
        fields = (
            'conversation_id', 'participants', 'participant_usernames',
            'participant_count', 'last_message', 'unread_count', 'created_at'
        )
        read_only_fields = ('conversation_id', 'created_at')
    
    def get_last_message(self, obj):
        """Get the last message in the conversation."""
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_id': str(last_message.message_id),
                'sender_username': last_message.sender.username,
                'message_body': last_message.message_body[:100] + ('...' if len(last_message.message_body) > 100 else ''),
                'sent_at': last_message.sent_at,
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for the current user."""
        # This is a placeholder - you might want to implement a read status system
        # For now, return 0
        return 0
    
    def create(self, validated_data):
        """Create conversation with participants."""
        participant_usernames = validated_data.pop('participant_usernames', [])
        conversation = Conversation.objects.create()
        
        # Add participants by username
        if participant_usernames:
            participants = CustomUser.objects.filter(username__in=participant_usernames)
            conversation.participants.set(participants)
        
        return conversation


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed conversation serializer with recent messages."""
    
    recent_messages = serializers.SerializerMethodField()
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ('recent_messages',)
    
    def get_recent_messages(self, obj):
        """Get the 10 most recent messages."""
        recent_messages = obj.messages.order_by('-sent_at')[:10]
        return MessageSerializer(recent_messages, many=True).data


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations."""
    
    participant_usernames = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        help_text="List of usernames to add as participants"
    )
    
    class Meta:
        model = Conversation
        fields = ('participant_usernames',)
    
    def validate_participant_usernames(self, value):
        """Validate that all usernames exist."""
        existing_users = CustomUser.objects.filter(username__in=value)
        existing_usernames = set(existing_users.values_list('username', flat=True))
        provided_usernames = set(value)
        
        missing_usernames = provided_usernames - existing_usernames
        if missing_usernames:
            raise serializers.ValidationError(
                f"The following users do not exist: {', '.join(missing_usernames)}"
            )
        
        return value
    
    def create(self, validated_data):
        """Create conversation with specified participants."""
        participant_usernames = validated_data['participant_usernames']
        
        conversation = Conversation.objects.create()
        
        # Add participants
        participants = CustomUser.objects.filter(username__in=participant_usernames)
        conversation.participants.set(participants)
        
        # Add the creator as a participant if not already included
        request = self.context.get('request')
        if request and request.user:
            conversation.participants.add(request.user)
        
        return conversation
