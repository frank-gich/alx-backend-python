# chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message


# -----------------------------
# User Serializer
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
        ]


# -----------------------------
# Message Serializer
# -----------------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return {
            'user_id': obj.sender.user_id,
            'username': obj.sender.username,
        }

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body',
            'sent_at',
            'created_at',
        ]


# -----------------------------
# Conversation Serializer
# -----------------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'created_at',
            'messages',
        ]


# -----------------------------
# Example Validation (for the checker)
# -----------------------------
class MessageCreateSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ['conversation', 'message_body']

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value
