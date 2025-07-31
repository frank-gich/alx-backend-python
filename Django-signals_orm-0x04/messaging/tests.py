from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification
from django.utils import timezone

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            password='testpass123'
        )
    
    def test_message_creates_notification(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        notification = Notification.objects.filter(
            user=self.receiver,
            message=message
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
        self.assertTrue(notification.created_at <= timezone.now())
    
    def test_notification_not_created_for_sender(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        notification = Notification.objects.filter(
            user=self.sender,
            message=message
        ).exists()
        
        self.assertFalse(notification)
