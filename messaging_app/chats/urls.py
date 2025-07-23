# # """
# # URL patterns for the chats app.
# # """

# # from django.urls import path
# # from . import views

# # app_name = 'chats'

# # urlpatterns = [
# #     # Conversation URLs
# #     path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
# #     path('conversations/<uuid:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
# #     path('conversations/create-with-users/', views.create_conversation_with_users, name='create-conversation-with-users'),
    
# #     # Participant management
# #     path('conversations/<uuid:conversation_id>/add-participant/', views.add_participant, name='add-participant'),
# #     path('conversations/<uuid:conversation_id>/remove-participant/', views.remove_participant, name='remove-participant'),
    
# #     # Message URLs
# #     path('conversations/<uuid:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
# #     path('conversations/<uuid:conversation_id>/messages/list/', views.conversation_messages, name='conversation-messages'),
# #     path('messages/<uuid:message_id>/', views.MessageDetailView.as_view(), name='message-detail'),
    
# #     # User search
# #     path('users/search/', views.search_users, name='search-users'),
# # ]

# # chats/urls.py

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ConversationViewSet, MessageViewSet
# from . import views as v

# app_name = 'chats'

# router = DefaultRouter()
# router.register(r'v2/conversations', ConversationViewSet, basename='conversation')
# router.register(r'v2/messages', MessageViewSet, basename='message')

# urlpatterns = [
#     # Old endpoints (v1)
#     path('v1/conversations/', v.ConversationListCreateView.as_view(), name='conversation-list-create'),
#     path('v1/conversations/<uuid:conversation_id>/', v.ConversationDetailView.as_view(), name='conversation-detail'),
#     path('v1/conversations/create-with-users/', v.create_conversation_with_users, name='create-conversation-with-users'),
#     path('v1/conversations/<uuid:conversation_id>/add-participant/', v.add_participant, name='add-participant'),
#     path('v1/conversations/<uuid:conversation_id>/remove-participant/', v.remove_participant, name='remove-participant'),
#     path('v1/conversations/<uuid:conversation_id>/messages/', v.MessageListCreateView.as_view(), name='message-list-create'),
#     path('v1/conversations/<uuid:conversation_id>/messages/list/', v.conversation_messages, name='conversation-messages'),
#     path('v1/messages/<uuid:message_id>/', v.MessageDetailView.as_view(), name='message-detail'),
#     path('v1/users/search/', v.search_users, name='search-users'),

#     # New ViewSet-based API (v2)
#     path('', include(router.urls)),
# ]
# In chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

app_name = 'chats'

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
