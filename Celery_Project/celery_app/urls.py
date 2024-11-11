from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet,TaskStatusAPIView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
    path('tasks/<uuid:task_id>/status/', TaskStatusAPIView.as_view(), name='task-status'),
]