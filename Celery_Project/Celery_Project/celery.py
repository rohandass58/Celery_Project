from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging
from django.conf import settings 

# Initialize logger for Celery-related events
logger = logging.getLogger(__name__)

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Celery_Project.settings')

# Create Celery app instance and configure it from Django settings
app = Celery('Celery_Project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from Django apps
app.autodiscover_tasks()

# Update Celery config for optimized worker management
app.conf.update(
    worker_prefetch_multiplier=1,  # Limit task prefetching to 1 to avoid overloading workers
    worker_max_tasks_per_child=1000,  # Restart workers after processing 1000 tasks to manage memory usage
    worker_max_memory_per_child=400000,  # Limit worker memory usage to 400MB to prevent memory leaks
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,  # Set hard execution time limit for tasks
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,  # Set soft execution time limit for tasks
    broker_pool_limit=10,  # Limit number of connections to the broker for better resource management
    worker_concurrency=4,  # Set number of worker processes for concurrent task execution
)
