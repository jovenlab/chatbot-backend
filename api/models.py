from django.db import models

class Conversation(models.Model):
    session_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=10)  # 'user' or 'rizal'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} | {self.session_id} | {self.sender}: {self.message[:30]}"



class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('rizal', 'Rizal'),
    )

    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} at {self.timestamp}: {self.message[:50]}"