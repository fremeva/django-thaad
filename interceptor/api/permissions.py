from rest_framework.permissions import BasePermission


class SessionOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.session.user == request.user
