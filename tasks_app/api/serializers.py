from django.contrib.auth.models import User
from rest_framework import serializers

from boards_app.models import Board
from tasks_app.models import Task


class TaskUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskCreateSerializer(serializers.ModelSerializer):
    board = serializers.IntegerField(write_only=True)
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)

    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def validate(self, attrs):
        board = self.context.get("board_instance")

        assignee_id = attrs.get("assignee_id")
        reviewer_id = attrs.get("reviewer_id")

        if assignee_id is not None:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"assignee_id": "Assignee not found."})

            if board.owner != assignee and assignee not in board.members.all():
                raise serializers.ValidationError(
                    {"assignee_id": "Assignee must be a board member."}
                )

            attrs["assignee"] = assignee

        if reviewer_id is not None:
            try:
                reviewer = User.objects.get(id=reviewer_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"reviewer_id": "Reviewer not found."})

            if board.owner != reviewer and reviewer not in board.members.all():
                raise serializers.ValidationError(
                    {"reviewer_id": "Reviewer must be a board member."}
                )

            attrs["reviewer"] = reviewer

        return attrs

    def create(self, validated_data):
        validated_data.pop("board", None)
        validated_data.pop("assignee_id", None)
        validated_data.pop("reviewer_id", None)

        board = self.context["board_instance"]

        task = Task.objects.create(
            board=board,
            title=validated_data["title"],
            description=validated_data.get("description", ""),
            status=validated_data["status"],
            priority=validated_data["priority"],
            assignee=validated_data.get("assignee"),
            reviewer=validated_data.get("reviewer"),
            due_date=validated_data.get("due_date"),
        )
        return task

    def get_comments_count(self, obj):
        return 0
