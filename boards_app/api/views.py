from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from boards_app.models import Board

from .permissions import IsBoardMemberOrOwner
from .serializers import BoardCreateSerializer, BoardDetailSerializer, BoardListSerializer


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()

    def get_queryset(self):
        user = self.request.user

        if self.action == "list":
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        return Board.objects.all()

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardListSerializer
