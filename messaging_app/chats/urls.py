"""
URL patterns for the chats app.
"""

from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    # Conversation URLs
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<uuid:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/create-with-users/', views.create_conversation_with_users, name='create-conversation-with-users'),
    
    # Participant management
    path('conversations/<uuid:conversation_id>/add-participant/', views.add_participant, name='add-participant'),
    path('conversations/<uuid:conversation_id>/remove-participant/', views.remove_participant, name='remove-participant'),
    
    # Message URLs
    path('conversations/<uuid:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('conversations/<uuid:conversation_id>/messages/list/', views.conversation_messages, name='conversation-messages'),
    path('messages/<uuid:message_id>/', views.MessageDetailView.as_view(), name='message-detail'),
    
    # User search
    path('users/search/', views.search_users, name='search-users'),
]