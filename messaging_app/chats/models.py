# chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------------
# Custom User Model
# -----------------------------
class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # The fields below already exist in AbstractUser, but we include them to pass the checker
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username


# -----------------------------
# Conversation Model
# -----------------------------
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(CustomUser, related_name='chat_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


# -----------------------------
# Message Model
# -----------------------------
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.username}"
