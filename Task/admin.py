from django.contrib import admin
from .models import Task, Comment, ContactMessage

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__username', 'room_number', 'issues_type', 'status', 'created_at']
    list_filter = ['status', 'issues_type', 'created_at']
    search_fields = ['user__email', 'room_number', 'description']
    ordering = ['-created_at']
    
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'task', 'created']
    list_filter = ['created', 'updated']
    search_fields = ['username', 'body']
    
    
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['name', 'email', 'phone', 'body', 'created_at']