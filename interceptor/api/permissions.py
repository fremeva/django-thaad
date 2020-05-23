from rest_framework.permissions import BasePermission

from interceptor.models import InterceptorSession, InterceptedRequest


class SessionOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, InterceptorSession):
            return obj.user == request.user
        if isinstance(obj, InterceptedRequest):
            return obj.session.user == request.user
        return False
