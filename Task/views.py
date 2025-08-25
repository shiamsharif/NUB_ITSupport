from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer, ContactMessageSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework import generics
from .permissions import IsItStuff  
from rest_framework.filters import SearchFilter
from django.core.mail import send_mail
from rest_framework import status
from Main import settings
from rest_framework.generics import ListAPIView




class TaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # auto-assign logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # updates existing task
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class TaskListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         tasks = Task.objects.all()
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data)


class DashboardTaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsItStuff]

    filterset_fields = ["status", "issues_type", "user"]

   
    search_fields = [
        "room_number", "task_name", "issues_type", "description",
        "user__username", "user__email",
    ]

    ordering_fields = ["created_at", "updated_at", "room_number", "task_name"]
    ordering = ["-created_at"]
    


class TaskListView(ListAPIView):

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    filterset_fields = ["status", "issues_type"]

    search_fields = [
        "room_number", "task_name", "issues_type",
        "description","computer_id", "monitor_id", "ups_id"
    ]

    ordering_fields = ["created_at", "updated_at", "room_number", "task_name"]
    ordering = ["-created_at"]
     

class PendingTaskListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsItStuff]

    def get_queryset(self):
        return Task.objects.filter(status='pending').order_by('-created_at')
        

class ResolvedTaskListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsItStuff]

    def get_queryset(self):
        return Task.objects.filter(status='resolved').order_by('-updated_at')


class TaskDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    

    
class TaskCommentsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        comments = Comment.objects.filter(task_id=task_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentViewSet(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.username != user:
            raise PermissionError("You do not have permission to modify this comment.")
        return comment

    def get(self, request, pk):
        
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        
        task = get_object_or_404(Task, pk=task_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, username=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)


class TaskUpdateStatusView(APIView):
    permission_classes = [IsItStuff]  # Custom permission for IT staff
    
    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # updates existing task
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ContactUsView(APIView):
    permission_classes = []  # Allow unauthenticated users

    # List of receivers you can update in future
    RECEIVER_EMAILS = ['shiam.sharif.07@gmail.com', 'sharif_41220100032@nub.ac.bd']

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            # save to database 
            serializer.save()

            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            body = serializer.validated_data['body']

            subject = f"New Contact Message from {name}"
            message = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            
            Message:
            {body}
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # from email
                self.RECEIVER_EMAILS,  # to emails
                fail_silently=False,
            )

            return Response({"message": "Your message has been sent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)