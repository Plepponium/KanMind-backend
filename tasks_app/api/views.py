from boards_app.models import Board
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from tasks_app.models import Task

from .serializers import TaskCreateSerializer, TaskUpdateSerializer


class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        board_id = request.data.get("board")

        if board_id is None:
            return Response(
                {"board": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")

        if board.owner != request.user and request.user not in board.members.all():
            raise PermissionDenied("You are not a member of this board.")

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


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id):
        try:
            task_id = int(task_id)
        except (ValueError, TypeError):
            raise ValidationError(
                {"task_id": "Task-ID must be a valid integer."})

        try:
            return Task.objects.select_related(
                "board", "assignee", "reviewer", "created_by"
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

    def check_board_membership(self, board, user):
        if board.owner != user and user not in board.members.all():
            raise PermissionDenied(
                "You must be a member of this board to update this task."
            )

    def check_delete_permission(self, task, user):
        is_creator = task.created_by == user
        is_board_owner = task.board.owner == user
        if not (is_creator or is_board_owner):
            raise PermissionDenied(
                "Only the creator of the task or the board owner can delete this task."
            )

    def patch(self, request, task_id):
        task = self.get_object(task_id)
        self.check_board_membership(task.board, request.user)

        data = request.data.copy() if hasattr(
            request.data, "copy") else dict(request.data)
        data.pop("board", None)

        serializer = TaskUpdateSerializer(
            task, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()

        response_serializer = TaskUpdateSerializer(updated_task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        task = self.get_object(task_id)
        self.check_delete_permission(task, request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
