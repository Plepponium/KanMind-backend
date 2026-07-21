from rest_framework.permissions import BasePermission


# class IsBoardMember(BasePermission):
#     def has_permission(self, request, view):
#         board = view.get_board()

#         if board is None:
#             return False

#         if board.owner == request.user:
#             return True

#         if request.user in board.members.all():
#             return True

#         return False
