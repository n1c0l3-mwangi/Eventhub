from django.db import models
from django.conf import settings
from django.core.mail import send_mail

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('in_app', 'In-App'),
        ('both', 'Both'),
    )
    
    CATEGORIES = (
        ('ticket', 'Ticket Purchase'),
        ('event', 'Event Update'),
        ('reminder', 'Event Reminder'),
        ('system', 'System Notification'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='in_app')
    category = models.CharField(max_length=20, choices=CATEGORIES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title