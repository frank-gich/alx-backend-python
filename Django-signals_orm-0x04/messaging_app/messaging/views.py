from django.contrib import admin
from .models import Message, Notification
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username']

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    # Ensure user is either sender or receiver
    if request.user not in [message.sender, message.receiver]:
        return render(request, 'messaging/403.html', status=403)
    
    history = message.history.all()
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })
