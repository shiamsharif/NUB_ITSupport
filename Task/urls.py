# tasks/urls.py
from django.urls import path
from .views import (
    TaskCreateView,
    TaskUpdateView,
    TaskListView,
    TaskDeleteView,
    TaskDetailView,
    TaskUpdateStatusView,
    CommentDetailView,
    ContactUsView,
)

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('listView/', TaskListView.as_view(), name='task-list'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='task-delete'),
    path('details/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('resolve/<int:pk>/', TaskUpdateStatusView.as_view(), name='task-resolve'),
    
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
]



