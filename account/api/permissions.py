from rest_framework.permissions import BasePermission


class IsCustomUserPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user) and request.user.is_active

    def has_object_permission(self, request, view, obj):
        return True
