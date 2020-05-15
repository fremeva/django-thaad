import json

from django.db.models import Q
from django.http import Http404
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from interceptor.models import InterceptedRequest, InterceptedFile, InterceptorSession


class InterceptorView(APIView):

    safe_meta = [
        'HTTP_USER_AGENT',
        'HTTP_ACCEPT',
        'HTTP_CACHE_CONTROL',
        'HTTP_ACCEPT_ENCODING',
        'HTTP_CONNECTION',
        'REMOTE_ADDR',
        'PATH_INFO',
        'REQUEST_METHOD',
        'CONTENT_LENGTH',
        'REMOTE_HOST',
        'CONTENT_TYPE'
    ]

    def __getattr__(self, item):
        if item in self.http_method_names:
            return self.create_intercepted_request
        return super(InterceptorView, self).__getattr__(item)

    def initial(self, request, *args, **kwargs):
        self.session = None

        if 'session_name' in kwargs.keys():
            self.session = self.get_session()

        return super(InterceptorView, self).initial(request, *args, **kwargs)

    def perform_authentication(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '')

        if len(token.split(' ')) > 1:
            token = token.split(' ')[-1]

        if token and self.session.session_token == token:
            request.user = self.session.user

    def get_session(self):
        short_name = self.kwargs.get('session_name', None)
        query = Q()
        if short_name:
            query &= Q(short_name=short_name)
        if self.request.user.is_authenticated:
            query &= Q(user=self.request.user)

        session = InterceptorSession.objects.filter(query)
        if session.exists():
            return session.first()

        raise Http404

    def get_request_metadata(self):
        return {
            key: value for (key, value) in self.request._request.META.items() if (
                    isinstance(value, str) and key in self.safe_meta
            )
        }

    def can_perform_creation(self, request, session):
        if session.requires_authentication and not request.user.is_authenticated:
            return False
        if session.requires_authentication and session.user != request.user:
            return False
        return True

    def create_intercepted_request(self, request, *args, **kwargs):
        """
        Intercepts all request to main URL and save it on database.
        """
        if self.can_perform_creation(request, self.session):

            request_meta = self.get_request_metadata()

            session_name = self.session.short_name if self.session else 'interceptor'
            request_path = request_meta.get('PATH_INFO').replace(f'/{session_name}', '')

            content_type = request.META.get('CONTENT_TYPE').split(';')[0]

            data = {key: value for key, value in request.data.items() if key not in request.FILES.keys()}

            intercepted_request = InterceptedRequest.objects.create(
                path=request_path,
                method=request.method,
                params=json.dumps(request.query_params),
                data=data if request.method.upper() != 'GET' else {},
                metadata=json.dumps(request_meta),
                headers=dict(request.headers),
                content_type=content_type,
                session=self.session
            )

            for key, file in request.FILES.items():
                self.create_intercepted_file(intercepted_request, key, file, self.session)

            return self.build_response(intercepted_request)

        else:
            return Response(data={'error': 'Unauthorized'}, status=HTTP_401_UNAUTHORIZED)

    def create_intercepted_file(self, intercepted_request, param, file, session=None):
        instance = InterceptedFile.objects.create(
            request=intercepted_request,
            parameter=param,
            filename=file.name,
            size=file.size
        )

        if session and session.saves_files:
            instance.file = file
            instance.save()

    def build_response(self, request):
        if self.session.mocks.filter(path=request.path, method=request.method.lower()).exists():
            mock = self.session.mocks.filter(path=request.path, method=request.method.lower()).first()
            headers = '{}' if not mock.response_headers else json.loads(mock.response_headers)

            return Response(
                data=json.loads(mock.response_body),
                status=mock.status_code,
                headers=headers
            )

        return Response(data={'status': 'OK'})
