from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from .models import Message, MessageHistory

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'messaging/delete_account.html')

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user not in [message.sender, message.receiver]:
        return render(request, 'messaging/403.html', status=403)
    
    history = message.history.all()
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })

@login_required
def threaded_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if request.user == other_user:
        return render(request, 'messaging/403.html', status=403)
    
    messages = Message.objects.filter(
        parent_message__isnull=True
    ).filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).select_related('sender', 'receiver').prefetch_related('replies')
    
    return render(request, 'messaging/threaded_conversation.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def unread_messages(request):
    messages = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/unread_messages.html', {
        'messages': messages
    })
