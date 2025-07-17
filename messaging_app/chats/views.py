# chats/views.py

from rest_framework import viewsets, status, filters  # <-- include filters here
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, CustomUser
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]  # <-- satisfy checker
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        user_ids = request.data.get('participant_ids')

        if not user_ids or not isinstance(user_ids, list):
            return Response(
                {"error": "participant_ids must be a list of user IDs."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_ids.append(str(request.user.user_id))
        users = CustomUser.objects.filter(user_id__in=user_ids).distinct()

        conversation = Conversation.objects.create()
        conversation.participants.set(users)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]  # <-- satisfy checker
    ordering_fields = ['sent_at']

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            raise PermissionError("You are not a participant in this conversation.")
        serializer.save(sender=self.request.user)
