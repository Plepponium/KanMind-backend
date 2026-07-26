from django.urls import path

from .views import TaskAssignedToMeView, TaskCommentsView, TaskCreateView, TaskDetailView, TaskReviewingView

urlpatterns = [
    path("", TaskCreateView.as_view(), name="task-create"),
    path("assigned-to-me/", TaskAssignedToMeView.as_view(), name="task-assigned-to-me"),
    path("reviewing/", TaskReviewingView.as_view(), name="task-reviewing"),
    path("<str:task_id>/comments/", TaskCommentsView.as_view(), name="task-comments-list"),
    path("<str:task_id>/", TaskDetailView.as_view(), name="task-detail"),
]
