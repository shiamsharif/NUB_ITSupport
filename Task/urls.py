# tasks/urls.py
from django.urls import path
from .views import (
    TaskCreateView,
    TaskUpdateView,
    DashboardTaskListView,
    TaskListView,
    TaskDeleteView,
    TaskDetailView,
    TaskUpdateStatusView,
    TaskCommentsListView,
    ContactUsView,
    CommentViewSet,
    PendingTaskListView,
    ResolvedTaskListView
)

urlpatterns = [
    path('dashboard-listView/', DashboardTaskListView.as_view(), name='dashboard-task-list'),
    path('pending-tasks/', PendingTaskListView.as_view(), name='pending-task-list'),
    path('resolved-tasks/', ResolvedTaskListView.as_view(), name='resolved-task-list'),
    
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path("listView/", TaskListView.as_view(), name="task-list"),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='task-delete'),
    path('details/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    
    path('resolve/<int:pk>/', TaskUpdateStatusView.as_view(), name='task-resolve'),
    
    path('tasks/<int:task_id>/comments/', TaskCommentsListView.as_view(), name='task-comments-list'),
    path('comments/<int:pk>/', CommentViewSet.as_view(), name='comment-detail'),  # GET, PUT, PATCH, DELETE
    path('<int:task_id>/comments/new/', CommentViewSet.as_view(), name='comment-create'),  # POST
    
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
]



