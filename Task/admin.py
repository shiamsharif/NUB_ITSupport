from django.contrib import admin
from .models import Task, Comment, ContactMessage


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0  
    readonly_fields = ['username', 'body', 'created', 'updated']
    can_delete = True  

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room_number', 'issues_type', 'status', 'created_at']
    list_filter = ['status', 'issues_type', 'created_at']
    search_fields = ['user', 'room_number', 'description']
    ordering = ['-created_at']
    inlines = [CommentInline] 
    
    # def user_username(self, obj):
    #     return obj.user.username
    # user_username.short_description = 'Username'
    
    
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
    readonly_fields = ['created_at']