"""
Custom permissions for the messaging app.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'participants'):
            # For Conversation model
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            # For Message model
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, 'sender'):
            # For Message model with sender field
            return obj.sender == request.user or request.user in obj.conversation.participants.all()
        
        return False


class IsMessageOwner(permissions.BasePermission):
    """
    Custom permission to only allow message owners to edit/delete their messages.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions: allow if user is participant in conversation
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'conversation'):
                return request.user in obj.conversation.participants.all()
            return False
        
        # Write permissions: only allow message owner
        return obj.sender == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in the conversation.
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users to create conversations
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow participants to access the conversation
        return request.user in obj.participants.all()


class CanViewMessages(permissions.BasePermission):
    """
    Permission to check if user can view messages in a conversation.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For message objects
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False


class CanSendMessage(permissions.BasePermission):
    """
    Permission to check if user can send messages to a conversation.
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user is participant in the conversation
        conversation_id = request.data.get('conversation') or view.kwargs.get('conversation_id')
        if conversation_id:
            from .models import Conversation  # Import here to avoid circular imports
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                return request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        
        return True  # Allow if no specific conversation is specified


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Combined permission for owner access or participant access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is the owner
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check if user is the sender
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True
        
        # Check if user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False