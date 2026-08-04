from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from tasks_app.models import Comment, Task

from .serializers import (
    TaskCommentCreateSerializer,
    TaskCommentSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer
)


class TaskAccessMixin:
    """Shared helpers for loading boards/tasks and checking board membership."""

    def get_board(self, board_id):
        """Return the board instance for the given id or raise a 404 error."""

        try:
            board_id = int(board_id)
        except (ValueError, TypeError):
            raise ValidationError(
                {"board": "Board-ID must be a valid integer."})

        try:
            return Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")

    def get_task(self, task_id):
        """Return the task instance for the given id or raise a 404 error."""

        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            raise ValidationError(
                {"task_id": "Task-ID must be a valid integer."})

        try:
            return Task.objects.select_related(
                "board",
                "board__owner",
                "assignee",
                "reviewer",
                "created_by",
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

    def check_board_membership(self, board, user):
        """Ensure the user is the board owner or a board member."""

        if board.owner != user and user not in board.members.all():
            raise PermissionDenied(
                "You must be a member of this board."
            )


class TaskCreateView(TaskAccessMixin, APIView):
    """View for creating tasks."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        board_id = request.data.get("board")
        if board_id is None:
            return Response(
                {"board": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        board = self.get_board(board_id)
        self.check_board_membership(board, request.user)

        serializer = TaskCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "board_instance": board,
            },
        )

        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        response_serializer = TaskCreateSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(TaskAccessMixin, APIView):
    """View for retrieving, updating, and deleting tasks."""

    permission_classes = [IsAuthenticated]

    def check_delete_permission(self, task, user):
        """Allow deletion only for the task creator or board owner."""

        is_creator = task.created_by == user
        is_board_owner = task.board.owner == user
        if not (is_creator or is_board_owner):
            raise PermissionDenied(
                "Only the creator of the task or the board owner can delete this task.")

    def patch(self, request, task_id):
        task = self.get_task(task_id)
        self.check_board_membership(task.board, request.user)
        data = request.data.copy() if hasattr(
            request.data, "copy") else dict(request.data)
        data.pop("board", None)
        serializer = TaskUpdateSerializer(task, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()
        response_serializer = TaskUpdateSerializer(updated_task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        task = self.get_task(task_id)
        self.check_delete_permission(task, request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskAssignedToMeView(APIView):
    """View for retrieving tasks assigned to the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user).select_related(
            "assignee", "reviewer").order_by("id")
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskReviewingView(APIView):
    """View for retrieving tasks where the authenticated user is the reviewer."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user).select_related(
            "assignee", "reviewer").order_by("id")
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCommentsView(TaskAccessMixin, APIView):
    """View for retrieving and creating comments for a specific task."""

    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = self.get_task(task_id)
        self.check_board_membership(task.board, request.user)

        comments = task.comments.select_related(
            "author").order_by("created_at")
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        task = self.get_task(task_id)
        self.check_board_membership(task.board, request.user)

        serializer = TaskCommentCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "task": task,
            },
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        response_serializer = TaskCommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TaskCommentDetailView(TaskAccessMixin, APIView):
    """View for deleting a specific comment on a task."""

    permission_classes = [IsAuthenticated]

    def get_comment(self, task, comment_id):
        """Return the comment for the given task or raise a 404 error."""

        try:
            comment_id = int(comment_id)
        except (ValueError, TypeError):
            raise ValidationError(
                {"comment_id": "Comment-ID must be a valid integer."})

        try:
            return Comment.objects.select_related("author", "task").get(
                id=comment_id,
                task=task,
            )
        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

    def check_delete_permission(self, comment, user):
        """Allow deletion only for the comment author."""

        if comment.author != user:
            raise PermissionDenied(
                "Only the author of this comment can delete it.")

    def delete(self, request, task_id, comment_id):
        task = self.get_task(task_id)
        comment = self.get_comment(task, comment_id)
        self.check_delete_permission(comment, request.user)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
