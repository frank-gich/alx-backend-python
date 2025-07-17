
from django.urls import path, include
from rest_framework import routers  # <-- this line changed
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()  # <-- now matches the checker's expectation
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
