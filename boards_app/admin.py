from django.contrib import admin

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin interface for the Board model."""

    list_display = ["id", "title", "owner"]
    search_fields = ["title", "owner__email", "owner__username"]
    filter_horizontal = ["members"]
