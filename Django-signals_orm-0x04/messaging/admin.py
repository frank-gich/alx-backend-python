from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'timestamp', 'edited', 'read']
    list_filter = ['timestamp', 'edited', 'read']
    search_fields = ['sender__username', 'receiver__username', 'content']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username']

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['message', 'old_content', 'edited_at', 'edited_by']
    list_filter = ['edited_at']
    search_fields = ['old_content', 'edited_by__username']
