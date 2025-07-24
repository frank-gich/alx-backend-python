from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import views

app_name = 'chats'

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat_view, name='chat'),
    path('message/', views.message_view, name='message'),
    path('public/', views.public_view, name='public'),
]
