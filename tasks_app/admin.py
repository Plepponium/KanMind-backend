from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for the Task model."""

    list_display = ("id", "title", "board__id", "board", "status",
                    "priority", "assignee", "reviewer", "due_date", "created_by", "board__owner")
    list_filter = ("status", "priority", "board")
    search_fields = ("title", "description")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for the Comment model."""

    list_display = ("id", "__str__", "author", "content", "task",
                    "task__id", "created_at")
    list_filter = ("task", "author")
    search_fields = ("content",)
