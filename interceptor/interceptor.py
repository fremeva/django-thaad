import re
from django.db.models import Q
from rest_framework.status import HTTP_200_OK
from rest_framework.utils import json

from interceptor.models import InterceptorSession


class SessionNotFoundError(Exception):
    pass


class BaseInterceptor:
    _meta = {}
    _data = {}
    _files = []
    path = None
    headers = None
    method = ''
    content_type = ''
    

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


class HttpInterceptor(BaseInterceptor):

    session = None

    def __init__(self, request, user=None):
        self.user = user
        self.method = request.method
        self.headers = request.headers

        self.set_path(request.META.get('PATH_INFO'))
        self.set_meta(request.META)

        self.extract_data_and_files(request.data, request.FILES)
        self.extract_content_type()
        
    def set_path(self, path):
        self.path = path.replace('/interceptor', '')
    
    def set_meta(self, meta):
        self._meta = {
            key: value for (key, value) in meta.items() if (
                    isinstance(value, str) and key in self.safe_meta
            )
        }

        return self._meta
    
    def extract_data_and_files(self, data, files):
        self._data = {key: value for key, value in data.items() if key not in files.keys()}
        self._files = files
        
    def extract_content_type(self):
        self.content_type = self._meta.get('CONTENT_TYPE').split(';')[0]

    def authenticate(self):
        return self.user

    def can_perform_creation(self):
        return True

    @property
    def data(self):
        return self._data

    @property
    def files(self):
        return self._files

    @property
    def meta(self):
        return self._meta

    def response_data(self):
        return {
            "data": {'status': 'You have sent a request, but we encourage you to create your own sessions!'},
            "status": HTTP_200_OK,
            "headers": {}
        }


class HttpSessionInterceptor(HttpInterceptor):
    session = None

    def __init__(self, request, session_name, user=None):
        query = Q(short_name=session_name)
        if user:
            query &= Q(user=user)

        session = InterceptorSession.objects.filter(query)

        if not session.exists():
            raise SessionNotFoundError()

        self.session = session.first()
        super(HttpSessionInterceptor, self).__init__(request, user=user)

    def authenticate(self):
        token = self.headers.get('AUTHORIZATION', '')
        if len(token.split(' ')) > 1:
            token = token.split(' ')[-1]

        if token and self.session.session_token == token:
            self.user = self.session.user
            return self.user

    def can_perform_creation(self):
        if self.session.requires_authentication and not self.user:
            return False
        if self.session.requires_authentication and self.session.user != self.user:
            return False
        return True

    def set_path(self, path):
        session_name = self.session.short_name
        regex = rf'.*\/{session_name}(?<!\/)'
        self.path = re.sub(regex, '', path)

    def response_data(self):
        mocks = self.session.mocks
        if mocks.filter(path=self.path, method=self.method.lower()).exists():
            mock = mocks.filter(path=self.path, method=self.method.lower()).first()
            headers = '{}' if not mock.response_headers else json.loads(mock.response_headers)

            return {
                "data": json.loads(mock.response_body),
                "status": mock.status_code,
                "headers": headers,
                "mock": mock
            }

        return super(HttpSessionInterceptor, self).response_data()
