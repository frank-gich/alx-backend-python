from django.urls import path
from . import views

urlpatterns = [
    path('message/<int:message_id>/history/', views.message_history, name='message_history'),
    path('delete-account/', views.delete_user, name='delete_user'),
    path('conversation/<int:user_id>/', views.threaded_conversation, name='threaded_conversation'),
    path('unread/', views.unread_messages, name='unread_messages'),
]
