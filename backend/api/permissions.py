from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response

User = get_user_model()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешения редактирования."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsUnauthorizedUser(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только неавторизованным пользователям.
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated
    def handle_no_permission(self):
        return Response({"detail": "Доступ запрещен для авторизованных пользователей."}, status=status.HTTP_403_FORBIDDEN)
