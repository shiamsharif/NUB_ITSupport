from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer, ContactMessageSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework import generics
from .permissions import IsItStuff  # Assuming you have a custom permission class for IT staff
from rest_framework.filters import SearchFilter
from django.core.mail import send_mail
from rest_framework import status
from Main import settings



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


class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    # comment section for each post
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, username=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.username != user:
            raise PermissionError("You do not have permission to modify this comment.")
        return comment

    def put(self, request, pk):
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()  # user and task don't change
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            comment = self.get_object(pk, request.user)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class TaskUpdateStatusView(APIView):
    permission_classes = [IsItStuff]  # Custom permission for IT staff
    
    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # updates existing task
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class TaskDashboardView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        queryset = Task.objects.all()

        # filter by status, issues_type, room number and user
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

      
        issues_type = self.request.query_params.get('issues_type')
        if issues_type:
            queryset = queryset.filter(issues_type=issues_type)

        
        room_number = self.request.query_params.get('room_number')
        if room_number:
            queryset = queryset.filter(room_number__icontains=room_number)

        
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user__user_type=user_type)

        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(task_name__icontains=search) |
                Q(room_number__icontains=search) | 
                Q(issues__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # --- Dashboard Stats ---
        pending_count = Task.objects.filter(status='pending').count()
        resolved_count = Task.objects.filter(status='resolved').count()

        return Response({
            'pending_count': pending_count,
            'resolved_count': resolved_count,
            'tasks': serializer.data
        })

    
    

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