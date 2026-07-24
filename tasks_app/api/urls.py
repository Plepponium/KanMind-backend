from django.urls import path

from .views import TaskCreateView, TaskDetailView

urlpatterns = [
    path("", TaskCreateView.as_view(), name="task-create"),
    path("<str:task_id>/", TaskDetailView.as_view(), name="task-detail"),
]
