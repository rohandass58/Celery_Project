from channels.generic.websocket import AsyncWebsocketConsumer
import json

# TaskStatusConsumer is a WebSocket consumer that handles real-time task status updates.
# It listens for updates on a specific task and sends them to the client connected via WebSocket.
class TaskStatusConsumer(AsyncWebsocketConsumer):
    
    # Called when the WebSocket connection is handshaken and established.
    async def connect(self):
        # Get the current user from the WebSocket scope (this is the authenticated user).
        self.user = self.scope["user"]
        
        # If the user is not authenticated, close the WebSocket connection immediately.
        if not self.user.is_authenticated:
            await self.close()
            return

        # Extract the task_id from the URL parameters. This is used to track which task the client is interested in.
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        
        # Create a unique group name based on the task_id so that only clients interested in this task get updates.
        self.group_name = f'task_{self.task_id}'

        # Add the current WebSocket connection (represented by channel_name) to the group corresponding to this task.
        # This enables the consumer to send task updates to all clients subscribed to the task.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection, allowing communication to start.
        await self.accept()

    # Called when the WebSocket connection is closed (e.g., the user disconnects).
    async def disconnect(self, close_code):
        # Remove the current WebSocket connection from the group, so it no longer receives updates.
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Called when a task status update is received in the WebSocket group for this task.
    # This method sends the status and result of the task to the WebSocket client.
    async def task_status_update(self, event):
        # Send the status and result data to the WebSocket client as a JSON object.
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'result': event['result']
        }))
