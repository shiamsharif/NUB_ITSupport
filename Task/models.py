# tasks/models.py
from django.db import models
from Account.models import CustomUser  

class Task(models.Model):
    ISSUE_CHOICES = [
        ('none', 'None'),
        ('software', 'Software Issues'),
        ('hardware', 'Hardware Issues'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    
    room_number = models.CharField(max_length=200)
    computer_id = models.CharField(max_length=100, blank=True, null=True)
    monitor_id = models.CharField(max_length=100, blank=True, null=True)
    ups_id = models.CharField(max_length=100, blank=True, null=True)

    task_name = models.CharField(max_length=100, blank=True, null=True)
    issues_type = models.CharField(max_length=10, choices=ISSUE_CHOICES, default='none')
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task({self.room_number}) - {self.issues_type} - {self.status}"
    
    
class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    username = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField()
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ['-created']
        
        
    def __str__(self):
        return f'Comment by {self.username.email} on Task {self.task.id}'
    
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
