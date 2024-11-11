from django.urls import re_path
from . import consumers

# WebSocket URL pattern for handling real-time updates for task status
websocket_urlpatterns = [
    re_path(r'ws/tasks/(?P<task_id>[^/]+)/$', consumers.TaskStatusConsumer.as_asgi()),
]
