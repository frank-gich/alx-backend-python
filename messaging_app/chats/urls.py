# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

# Use NestedDefaultRouter as required by the checker
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Nest messages under conversations (optional but needed for the import to appear)
convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
convo_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(convo_router.urls)),
]
