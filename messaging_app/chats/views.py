"""
Views for handling conversations and messages with proper authentication.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from .models import CustomUser, Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationDetailSerializer,
    MessageCreateSerializer
)
from .permissions import (
    IsConversationParticipant, 
    CanSendMessage, 
    IsMessageOwner,
    CanViewMessages
)


class MessagePagination(PageNumberPagination):
    """Custom pagination for messages."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    List user's conversations or create a new conversation.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return conversations where user is a participant."""
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            last_message_time=Max('messages__sent_at')
        ).order_by('-last_message_time', '-created_at')
    
    def perform_create(self, serializer):
        """Create conversation and add current user as participant."""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a conversation.
    Only participants can access the conversation.
    """
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    lookup_field = 'conversation_id'
    
    def get_queryset(self):
        """Return conversations where user is a participant."""
        return Conversation.objects.filter(participants=self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    List messages in a conversation or send a new message.
    """
    permission_classes = [permissions.IsAuthenticated, CanViewMessages]
    pagination_class = MessagePagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(
            Conversation, 
            conversation_id=conversation_id,
            participants=self.request.user
        )
        return Message.objects.filter(conversation=conversation).order_by('-sent_at')
    
    def perform_create(self, serializer):
        """Create message with current user as sender."""
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(
            Conversation,
            conversation_id=conversation_id,
            participants=self.request.user
        )
        serializer.save(sender=self.request.user, conversation=conversation)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a message.
    Only message sender can modify their messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsMessageOwner]
    lookup_field = 'message_id'
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        return Message.objects.filter(
            conversation__participants=self.request.user
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_conversation_with_users(request):
    """
    Create a conversation with specific users.
    """
    usernames = request.data.get('usernames', [])
    
    if not usernames:
        return Response(
            {'error': 'At least one username is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get users by username
    users = CustomUser.objects.filter(username__in=usernames)
    if len(users) != len(usernames):
        found_usernames = users.values_list('username', flat=True)
        missing_usernames = set(usernames) - set(found_usernames)
        return Response(
            {'error': f'Users not found: {list(missing_usernames)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, *users)
    
    serializer = ConversationDetailSerializer(conversation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_participant(request, conversation_id):
    """
    Add a participant to an existing conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        conversation_id=conversation_id,
        participants=request.user
    )
    
    username = request.data.get('username')
    if not username:
        return Response(
            {'error': 'Username is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if user in conversation.participants.all():
        return Response(
            {'error': 'User is already a participant'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    conversation.participants.add(user)
    
    serializer = ConversationDetailSerializer(conversation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_participant(request, conversation_id):
    """
    Remove a participant from a conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        conversation_id=conversation_id,
        participants=request.user
    )
    
    username = request.data.get('username')
    if not username:
        return Response(
            {'error': 'Username is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if user not in conversation.participants.all():
        return Response(
            {'error': 'User is not a participant'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Don't allow removing the last participant
    if conversation.participants.count() <= 1:
        return Response(
            {'error': 'Cannot remove the last participant'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    conversation.participants.remove(user)
    
    serializer = ConversationDetailSerializer(conversation)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    """
    Search for users by username or email.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {'error': 'Search query is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    users = CustomUser.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(user_id=request.user.user_id)[:10]  # Limit to 10 results
    
    user_data = [{
        'user_id': str(user.user_id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    } for user in users]
    
    return Response({'users': user_data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_messages(request, conversation_id):
    """
    Get messages for a specific conversation with pagination.
    """
    conversation = get_object_or_404(
        Conversation,
        conversation_id=conversation_id,
        participants=request.user
    )
    
    messages = Message.objects.filter(conversation=conversation).order_by('-sent_at')
    
    paginator = MessagePagination()
    paginated_messages = paginator.paginate_queryset(messages, request)
    
    serializer = MessageSerializer(paginated_messages, many=True)
    return paginator.get_paginated_response(serializer.data)