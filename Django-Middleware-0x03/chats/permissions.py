from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access messages.
    Requires authentication and conversation participation.
    Enhanced to work with filtering and pagination.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow participants of a conversation
        to view, edit, or delete messages in that conversation.
        """
        # If the object is a Message, check if user is participant of its conversation
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
        # If the object is a Conversation, use it directly
        elif hasattr(obj, 'participants'):
            conversation = obj
        else:
            return False
        
        # Check if the authenticated user is a participant in the conversation
        return conversation.participants.filter(id=request.user.id).exists()
    
    def has_conversation_permission(self, request, conversation_id):
        """
        Helper method to check if user is participant of a specific conversation.
        Can be used in viewsets for additional checks.
        """
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            return conversation.participants.filter(id=request.user.id).exists()
        except:
            return False
    
    def filter_queryset_for_user(self, request, queryset):
        """
        Helper method to filter queryset to only include messages from 
        conversations where the user is a participant.
        """
        if not request.user.is_authenticated:
            return queryset.none()
        
        return queryset.filter(conversation__participants=request.user).distinct()


class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission that allows message owners to update/delete their messages,
    and all participants to view messages.
    Enhanced for filtering and bulk operations.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        For filtering and listing, this is sufficient.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for all conversation participants.
        Write permissions (PUT, PATCH, DELETE) only for message owner.
        """
        # Check if user is participant of the conversation
        if not obj.conversation.participants.filter(id=request.user.id).exists():
            return False
        
        # Read permissions for all participants (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions (PUT, PATCH, DELETE) only for message owner
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        # POST is handled at the view level
        return True
    
    def get_filtered_queryset(self, request, queryset):
        """
        Return messages from conversations where user is a participant.
        This method helps with filtering at the queryset level.
        """
        if not request.user.is_authenticated:
            return queryset.none()
        
        return queryset.filter(
            Q(conversation__participants=request.user)
        ).distinct()


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission for conversation-level operations.
    Only participants can access conversation details.
    Enhanced for filtering multiple conversations.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Only allow participants to access conversation.
        """
        return obj.participants.filter(id=request.user.id).exists()
    
    def get_user_conversations(self, request, queryset):
        """
        Filter conversations to only those where user is a participant.
        """
        if not request.user.is_authenticated:
            return queryset.none()
        
        return queryset.filter(participants=request.user).distinct()


class CanCreateMessage(permissions.BasePermission):
    """
    Permission class to check if user can create messages in a conversation.
    Enhanced with better error handling for filtering contexts.
    Handles PUT, PATCH, DELETE methods for message modification.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and is participant of the target conversation.
        Handle different HTTP methods (POST, PUT, PATCH, DELETE).
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For POST requests, check conversation_id in request data
        if request.method == 'POST':
            conversation_id = request.data.get('conversation_id') or request.data.get('conversation')
            if conversation_id:
                try:
                    conversation = get_object_or_404(Conversation, id=conversation_id)
                    return conversation.participants.filter(id=request.user.id).exists()
                except:
                    return False
        
        # For PUT, PATCH, DELETE - permission will be checked at object level
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions for PUT, PATCH, DELETE operations.
        Only message sender can modify/delete their messages.
        All participants can view messages.
        """
        # Ensure user is participant of the conversation
        if not obj.conversation.participants.filter(id=request.user.id).exists():
            return False
        
        # For modification operations (PUT, PATCH, DELETE), only message owner allowed
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        # For read operations, all participants allowed
        return True

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access messages.
    Requires authentication and conversation participation.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow participants of a conversation
        to view, edit, or delete messages in that conversation.
        """
        # If the object is a Message, check if user is participant of its conversation
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
        # If the object is a Conversation, use it directly
        elif hasattr(obj, 'participants'):
            conversation = obj
        else:
            return False
        
        # Check if the authenticated user is a participant in the conversation
        return conversation.participants.filter(id=request.user.id).exists()
    
    def has_conversation_permission(self, request, conversation_id):
        """
        Helper method to check if user is participant of a specific conversation.
        Can be used in viewsets for additional checks.
        """
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            return conversation.participants.filter(id=request.user.id).exists()
        except:
            return False


class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission that allows message owners to update/delete their messages,
    and all participants to view messages.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for all conversation participants.
        Write permissions only for message owner.
        """
        # Check if user is participant of the conversation
        if not obj.conversation.participants.filter(id=request.user.id).exists():
            return False
        
        # Read permissions for all participants
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for message owner
        return obj.sender == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission for conversation-level operations.
    Only participants can access conversation details.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Only allow participants to access conversation.
        """
        return obj.participants.filter(id=request.user.id).exists()


class CanCreateMessage(permissions.BasePermission):
    """
    Permission class to check if user can create messages in a conversation.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and is participant of the target conversation.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For POST requests, check conversation_id in request data
        if request.method == 'POST':
            conversation_id = request.data.get('conversation_id') or request.data.get('conversation')
            if conversation_id:
                try:
                    conversation = get_object_or_404(Conversation, id=conversation_id)
                    return conversation.participants.filter(id=request.user.id).exists()
                except:
                    return False
        
        return True
