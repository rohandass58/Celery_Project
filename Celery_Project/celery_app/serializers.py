from rest_framework import serializers
from .models import Task
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # Specify the fields to be serialized and which are read-only
        fields = ['id', 'name', 'description', 'status', 'scheduled_time', 
                 'created_at', 'updated_at', 'result', 'error_message']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 
                          'result', 'error_message']

    def validate_scheduled_time(self, value):
        # Ensure that the scheduled time is not in the past
        if value < timezone.now():
            raise serializers.ValidationError("Cannot schedule tasks in the past")
        return value
