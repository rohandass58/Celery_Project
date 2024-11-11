# settings.py
CELERY_TASK_MAX_RETRIES = 5  # Maximum number of retries for Celery tasks before they are considered failed.

# tasks.py
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded  # This exception is raised when the task exceeds its time limit.
from django.utils import timezone
from .models import Task  # Import the Task model to update task status and result.
import logging
import statsd  # For integrating with StatsD to track task metrics.

# Set up logging and statsd client for tracking task metrics
logger = logging.getLogger(__name__)  # Create a logger for this file.
statsd_client = statsd.StatsClient('localhost', 8125)  # Connect to the StatsD server running locally on port 8125.

@shared_task(bind=True, max_retries=CELERY_TASK_MAX_RETRIES)  # Bind the task to the current instance and set max retries from settings.
def process_data_task(self, task_id):
    """
    This is the main Celery task that processes data. It updates the task status and 
    retries with exponential backoff in case of failure.
    """

    try:
        # Fetch the task from the database using the task ID
        task = Task.objects.get(id=task_id)
        
        # Set the status of the task to "RUNNING" when the processing starts
        task.status = 'RUNNING'
        task.save()

        # Simulate data processing (replace this with actual logic)
        # Add your actual data processing code here
        
        # Once processing is done, update task status to "COMPLETED"
        task.status = 'COMPLETED'
        task.result = {'message': 'Data processed successfully'}
        task.save()

    except SoftTimeLimitExceeded:
        # Handle the scenario where the task exceeds its time limit
        task.status = 'FAILED'
        task.error_message = 'Task timed out'
        task.save()

        # Log and track the timeout metric
        statsd_client.incr('tasks.timeout')  # Increment the timeout metric in StatsD
        raise  # Reraise the exception so that Celery handles the failure.

    except Exception as exc:
        # Handle any other exceptions that occur during task processing
        task.status = 'FAILED'
        task.error_message = str(exc)  # Capture the error message
        task.retry_count += 1  # Increment the retry count for the task
        task.save()

        # If the retry count is less than the maximum retries, schedule the task for a retry
        if task.retry_count < task.max_retries:
            countdown = 60 * 2 ** task.retry_count  # Exponential backoff: retry after increasing intervals
            logger.warning(f'Task {task_id} failed. Retrying in {countdown} seconds...')  # Log the retry
            statsd_client.incr('tasks.retries')  # Track retry attempts in StatsD
            raise self.retry(exc=exc, countdown=countdown)  # Retry the task with the exponential backoff

        else:
            # If the maximum number of retries is reached, log the failure and track it in StatsD
            logger.error(f'Task {task_id} failed and reached max retries.')
            statsd_client.incr('tasks.max_retries_reached')  # Track max retries reached metric in StatsD
            raise  # Reraise the exception to indicate task failure
