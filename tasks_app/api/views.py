from boards_app.models import Board
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TaskCreateSerializer


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
