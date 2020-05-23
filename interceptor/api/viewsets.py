from django.conf import settings
from rest_framework import authentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from interceptor.api.permissions import SessionOwnerPermission
from interceptor.api.serializers import InterceptedRequestModelSerializer, InterceptorSessionSerializer
from interceptor.models import InterceptedRequest, InterceptorSession


class AuthenticatorMixin:
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]

    def get_authenticators(self):
        authenticators = super(AuthenticatorMixin, self).get_authenticators()
        if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
            authenticators.append(authentication.TokenAuthentication)
        return authenticators


class RendererHTMLOnDebugMixin:
    def get_renderers(self):
        renderers = super(RendererHTMLOnDebugMixin, self).get_renderers()
        if not settings.DEBUG:
            renderers = [r for r in renderers if r.media_type != 'text/html']
        return renderers


class InterceptedRequestModelListViewset(
    ListModelMixin,
    RetrieveModelMixin,
    AuthenticatorMixin,
    RendererHTMLOnDebugMixin,
    GenericViewSet
):
    queryset = InterceptedRequest.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = InterceptedRequestModelSerializer
    permission_classes = [IsAuthenticated, SessionOwnerPermission]

    def get_user_sessions(self):
        return InterceptorSession.objects.filter(user=self.request.user).values('id')

    def get_queryset(self):
        """
        Get only intercepted request for sessions created for authenticated user.
        """
        qs = super(InterceptedRequestModelListViewset, self).get_queryset()

        if 'session_id' in self.request.query_params:
            session_id = self.request.query_params.get('session_id')
            return qs.filter(session_id__in=self.get_user_sessions().filter(id=session_id)).order_by('created_at')

        return qs.filter(session_id__in=self.get_user_sessions()).order_by('created_at')


class InterceptorSessionViewset(AuthenticatorMixin, RendererHTMLOnDebugMixin, ModelViewSet):
    queryset = InterceptorSession.objects.all()
    serializer_class = InterceptorSessionSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated, SessionOwnerPermission]

    def get_queryset(self):
        qs = super(InterceptorSessionViewset, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
