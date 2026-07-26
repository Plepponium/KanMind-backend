from django.contrib.auth.models import User
from rest_framework import serializers

from tasks_app.models import Comment, Task


class BoardMemberValidationMixin:

    @property
    def board(self):
        if self.instance is not None:
            return self.instance.board
        return self.context["board_instance"]

    def _validate_member(self, user_id, field_name):
        if user_id is None:
            return None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {field_name:
                    f"{field_name.replace('_id', '').capitalize()} not found."}
            )
        if self.board.owner != user and user not in self.board.members.all():
            raise serializers.ValidationError(
                {field_name: f"{field_name.replace('_id', '').capitalize()} must be a board member."}
            )
        return user


class TaskUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskListSerializer(serializers.ModelSerializer):
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
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskCreateSerializer(BoardMemberValidationMixin, serializers.ModelSerializer):
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
        attrs["assignee"] = self._validate_member(
            attrs.get("assignee_id"), "assignee_id")
        attrs["reviewer"] = self._validate_member(
            attrs.get("reviewer_id"), "reviewer_id")
        return attrs

    def create(self, validated_data):
        for key in ("board", "assignee_id", "reviewer_id"):
            validated_data.pop(key, None)
        task = Task.objects.create(
            board=self.board, created_by=self.context["request"].user, **validated_data)
        return task

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskUpdateSerializer(BoardMemberValidationMixin, serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
        ]

    def validate(self, attrs):
        if "assignee_id" in self.initial_data:
            attrs["assignee"] = self._validate_member(
                attrs.get("assignee_id"), "assignee_id")
        if "reviewer_id" in self.initial_data:
            attrs["reviewer"] = self._validate_member(
                attrs.get("reviewer_id"), "reviewer_id")
        return attrs

    def update(self, instance, validated_data):
        for key in ("assignee_id", "reviewer_id"):
            validated_data.pop(key, None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip()


class TaskCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content"]

    def create(self, validated_data):
        return Comment.objects.create(
            task=self.context["task"],
            author=self.context["request"].user,
            content=validated_data["content"],
        )