"""
ASGI config for Celery_Project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from Celery_Project.celery import app as celery_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Celery_Project.settings')

application = get_asgi_application()
celery_app.set_default()
