from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status",
                    "priority", "assignee", "reviewer", "due_date", "created_by", "board__owner")
    list_filter = ("status", "priority", "board")
    search_fields = ("title", "description")
