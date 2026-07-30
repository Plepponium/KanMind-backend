from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow access to board members and the board owner."""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True

        if request.user in obj.members.all():
            return True

        return False


class IsBoardOwner(BasePermission):
    """Allow access only to the board owner."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
