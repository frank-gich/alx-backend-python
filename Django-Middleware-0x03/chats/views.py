from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_403_FORBIDDEN

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import (
    IsParticipantOfConversation,
    IsMessageOwnerOrParticipant,
    IsConversationParticipant,
    CanCreateMessage
)
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Only participants can access conversation details.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__username', 'participants__email', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant.
        """
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        
        return Conversation.objects.filter(
            participants=self.request.user
        ).distinct().prefetch_related('participants', 'messages')
    
    def perform_create(self, serializer):
        """
        Automatically add the current user as a participant when creating a conversation.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation.
        Only participants can access messages.
        """
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation.
        Only existing participants can add new participants.
        """
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            return Response(
                {'detail': 'You are not allowed to add participants to this conversation.'},
                status=HTTP_403_FORBIDDEN
        )

        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_to_add = User.objects.get(id=user_id)
            
            if conversation.participants.filter(id=user_id).exists():
                return Response(
                    {'error': 'User is already a participant'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversation.participants.add(user_to_add)
            return Response(
                {'message': 'Participant added successfully'}, 
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation.
        Users can remove themselves, or existing participants can remove others.
        """
        conversation = self.get_object()
        if str(user_id) != str(request.user.id) and request.user not in conversation.participants.all():
            return Response(
                {'detail': 'You are not allowed to remove participants from this conversation.'},
                status=HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Users can remove themselves or remove others if they're participants
        if str(user_id) != str(request.user.id):
            # Check if user being removed is actually a participant
            if not conversation.participants.filter(id=user_id).exists():
                return Response(
                    {'error': 'User is not a participant'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        conversation.participants.remove(user_id)
        return Response(
            {'message': 'Participant removed successfully'}, 
            status=status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Only conversation participants can view messages.
    Only message owners can update/delete their messages.
    Includes pagination (20 messages per page) and comprehensive filtering.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageOwnerOrParticipant, CanCreateMessage]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['timestamp', 'sender__username', 'conversation__id']
    ordering = ['-timestamp']  # Most recent messages first
    
    def get_queryset(self):
        """
        Return messages from conversations where the current user is a participant.
        """
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').prefetch_related('conversation__participants')
    
    def perform_create(self, serializer):
        """
        Set the sender to the current user and validate conversation participation.
        """
        conversation_id = self.request.data.get('conversation_id') or self.request.data.get('conversation')
        
        if not conversation_id:
            raise PermissionDenied("Conversation ID is required")
        
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id)
        except:
            raise PermissionDenied("Invalid conversation")
        
        # Check if user is participant of the conversation
        if not conversation.participants.filter(id=self.request.user.id).exists():
            return Response(
                {'detail': 'You are not a participant of this conversation.'},
                status=HTTP_403_FORBIDDEN
            )

        serializer.save(sender=self.request.user, conversation=conversation)
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        """
        if self.action == 'create':
            permission_classes = [CanCreateMessage]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsMessageOwnerOrParticipant]
        else:
            permission_classes = [IsParticipantOfConversation]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        """
        Get all messages sent by the current user.
        """
        messages = self.get_queryset().filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def filtered_messages(self, request):
        """
        Get filtered messages with advanced filtering options.
        Supports all MessageFilter options with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation_history(self, request):
        """
        Get paginated message history for a specific conversation.
        Requires conversation_id parameter and supports time range filtering.
        """
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            
            # Check if user is participant
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response(
                    {'detail': 'You are not a participant of this conversation.'},
                    status=HTTP_403_FORBIDDEN
                )

            
            # Get messages for this conversation
            queryset = self.get_queryset().filter(conversation=conversation)
            
            # Apply additional filtering from query parameters
            filterset = MessageFilter(request.query_params, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
            
            # Paginate results
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search_messages(self, request):
        """
        Search messages across all user's conversations with pagination.
        Supports text search, date ranges, and user filtering.
        """
        search_query = request.query_params.get('q', '')
        
        if not search_query:
            return Response(
                {'error': 'Search query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start with user's accessible messages
        queryset = self.get_queryset()
        
        # Apply search across content and sender information
        from django.db.models import Q
        queryset = queryset.filter(
            Q(message_body__icontains=search_query) |
            Q(sender__username__icontains=search_query) |
            Q(sender__first_name__icontains=search_query) |
            Q(sender__last_name__icontains=search_query)
        )
        
        # Apply additional filters
        filterset = MessageFilter(request.query_params, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['search_query'] = search_query
            return Response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'search_query': search_query,
            'results': serializer.data
        })

# chats/views.py
"""
Sample views to test the middleware functionality.
Add these to your Django app's views.py file.
"""
@csrf_exempt
def chat_view(request):
    """
    Simple chat endpoint for testing middleware.
    Accepts both GET and POST requests.
    """
    if request.method == 'GET':
        return JsonResponse({
            'message': 'Chat endpoint accessed successfully',
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'timestamp': str(request.GET.get('timestamp', 'No timestamp'))
        })
    
    elif request.method == 'POST':
        # Handle POST requests (chat messages)
        message = request.POST.get('message', '')
        
        if not message:
            try:
                # Handle JSON data
                data = json.loads(request.body.decode('utf-8'))
                message = data.get('message', '')
            except:
                message = 'No message content'
        
        return JsonResponse({
            'status': 'Message received',
            'message': message,
            'user': request.user.username if request.user.is_authenticated else 'Anonymous'
        })

@csrf_exempt
def message_view(request):
    """
    Another endpoint for testing middleware.
    """
    return JsonResponse({
        'endpoint': 'message',
        'method': request.method,
        'user': request.user.username if request.user.is_authenticated else 'Anonymous'
    })

def public_view(request):
    """
    Public endpoint that should not be restricted by role middleware.
    """
    return JsonResponse({
        'message': 'This is a public endpoint',
        'accessible': 'by everyone'
    })

