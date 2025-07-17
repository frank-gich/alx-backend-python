# chats/serializers.py

from rest_framework import serializers
from .models import CustomUser, Conversation, Message


# -----------------------------
# User Serializer
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
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
    sender = UserSerializer(read_only=True)  # nested sender info

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
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'created_at',
            'messages',  # nested messages
        ]
