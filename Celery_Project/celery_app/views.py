from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Task
from .serializers import TaskSerializer
from .tasks import process_data_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.views import APIView

class TaskViewSet(viewsets.ModelViewSet):
    # Serializer class to handle task data
    serializer_class = TaskSerializer
    # Restrict access to authenticated users only
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return tasks associated with the currently authenticated user
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # This method is called when creating a new task
        task = serializer.save(user=self.request.user)
        
        # Schedule the Celery task at the specified scheduled time or immediately if it's in the past
        scheduled_time = task.scheduled_time
        eta = max(scheduled_time, timezone.now())
        
        # Apply the Celery task asynchronously
        celery_task = process_data_task.apply_async(
            args=[str(task.id)],  # Pass the task ID as an argument to the Celery task
            eta=eta  # Set the exact time when the task should be executed
        )
        
        # Save the Celery task ID and update task status
        task.celery_task_id = celery_task.id
        task.status = 'SCHEDULED'
        task.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        # Action to cancel a task
        task = self.get_object()
        
        # Check if the task can be cancelled based on its current state
        if not hasattr(task, 'can_cancel') or not task.can_cancel():
            return Response(
                {'error': 'Task cannot be cancelled in its current state'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If the task has a Celery task ID, revoke the task (terminate it)
        if task.celery_task_id:
            from celery.task.control import revoke
            revoke(task.celery_task_id, terminate=True)

        # Update the task status to 'CANCELLED'
        task.status = 'CANCELLED'
        task.save()
        
        # Respond to the client that the task has been successfully cancelled
        return Response({'status': 'Task cancelled'})

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        # Action to retry a task
        task = self.get_object()
        
        # Check if the task can be retried
        if not hasattr(task, 'can_retry') or not task.can_retry():
            return Response(
                {'error': 'Task cannot be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset task status and increase the retry count
        task.status = 'SCHEDULED'
        task.retry_count += 1
        task.save()

        # Schedule a new Celery task with a countdown based on the retry count
        celery_task = process_data_task.apply_async(
            args=[str(task.id)],  # Pass the task ID as an argument to the Celery task
            countdown=60 * task.retry_count  # Increase countdown time with each retry
        )
        
        # Save the new Celery task ID and update the task status
        task.celery_task_id = celery_task.id
        task.save()

        # Respond to the client that the task is scheduled for retry
        return Response({'status': 'Task scheduled for retry'})
    

# Function to send real-time updates about the task status to connected clients via WebSockets
def send_realtime_update(task_id, status, result=None):
    channel_layer = get_channel_layer()
    # Send a message to the WebSocket group for the specific task
    async_to_sync(channel_layer.group_send)(
        f"task_{task_id}",  # Group name based on task ID
        {"type": "update_task_status", "status": status, "result": result}
    )


class TaskStatusAPIView(APIView):
    # Restrict access to authenticated users only
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        # Retrieve the task by ID, ensuring that the task belongs to the current user
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        # Check if the authenticated user is the owner of the task
        if task.user != request.user:
            return Response(
                {'error': 'You are not authorized to access this task'},
                status=403  # Return Forbidden if the user doesn't own the task
            )

        # Prepare the task data to return as JSON
        data = {
            'id': str(task.id),  # Convert task ID to string
            'status': task.status,
            'result': task.result,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),  # Convert timestamps to ISO format
            'updated_at': task.updated_at.isoformat(),
        }
        # Return the task data in the response
        return Response(data)
