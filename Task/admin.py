from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__first_name', 'room_number', 'issues_type', 'status', 'created_at']
    list_filter = ['status', 'issues_type', 'created_at']
    search_fields = ['user__email', 'room_number', 'description']
    ordering = ['-created_at']