import os
from django.core.wsgi import get_wsgi_application
from Celery_Project.celery import app as celery_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Celery_Project.settings')

application = get_wsgi_application()
celery_app.set_default()
