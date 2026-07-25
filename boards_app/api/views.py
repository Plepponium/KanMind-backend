from django.db.models import Q, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from boards_app.models import Board

from .permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import BoardCreateSerializer, BoardDetailSerializer, BoardListSerializer, BoardUpdateSerializer


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()

    def get_queryset(self):
        user = self.request.user

        if self.action == "list":
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks", filter=Q(tasks__status="to-do"), distinct=True
                ),
                tasks_high_prio_count=Count(
                    "tasks", filter=Q(tasks__priority="high"), distinct=True
                ),
            ).distinct()

        return Board.objects.all()

    def get_permissions(self):
        if self.action in ["retrieve", "partial_update"]:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardListSerializer
