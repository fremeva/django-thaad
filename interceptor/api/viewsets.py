from django.conf import settings
from rest_framework import authentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from interceptor.api.permissions import SessionOwnerPermission
from interceptor.api.serializers import InterceptedRequestModelSerializer
from interceptor.models import InterceptedRequest, InterceptorSession


class InterceptedRequestModelListViewset(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    queryset = InterceptedRequest.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = InterceptedRequestModelSerializer
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [IsAuthenticated, SessionOwnerPermission]

    def get_user_sessions(self):
        return InterceptorSession.objects.filter(user=self.request.user).values('id')

    def get_queryset(self):
        """
        Get only intercepted request for sessions created for authenticated user.
        """
        qs = super(InterceptedRequestModelListViewset, self).get_queryset()
        return qs.filter(session_id__in=self.get_user_sessions())

    def get_authenticators(self):
        authenticators = super(InterceptedRequestModelListViewset, self).get_authenticators()
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            authenticators.append(authentication.TokenAuthentication)
        return authenticators

    def get_renderers(self):
        renderers = super(InterceptedRequestModelListViewset, self).get_renderers()
        if not settings.DEBUG:
            renderers = [r for r in renderers if r.media_type != 'text/html']
        return renderers
