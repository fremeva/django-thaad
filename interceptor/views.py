import json
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK
from rest_framework.views import APIView

from interceptor.interceptor import HttpSessionInterceptor, HttpInterceptor, SessionNotFoundError
from interceptor.models import InterceptedRequest, InterceptedFile


class HTTPInterceptorView(APIView):
    """
    HTTPInterceptorView is a basic view that intercepts any request without having an existing session
    """

    interceptor_class = HttpInterceptor
    interceptor = None

    def __getattr__(self, item):
        if item in self.http_method_names:
            return self.intercept
        try:
            return super(HTTPInterceptorView, self).__getattr__(item)
        except AttributeError:
            raise AttributeError(item)

    def options(self, request, *args, **kwargs):
        # TODO: Check cors and if cors do not intercept here
        cors = False
        if cors:
            if self.metadata_class is None:
                return self.http_method_not_allowed(request, *args, **kwargs)
            data = self.metadata_class().determine_metadata(request, self)
            return Response(data, status=HTTP_200_OK)
        else:
            return self.intercept(request, *args, **kwargs)

    def get_interceptor_class(self):
        assert self.interceptor_class is not None, (
                "'%s' should either include a `interceptor_class` attribute, "
                "or override the `get_interceptor_class()` method."
                % self.__class__.__name__
        )

        return self.interceptor_class

    def get_interceptor_class_kwargs(self, **kwargs):
        kwargs = kwargs or {}

        kwargs.update({
            'request': self.request,
        })
        return kwargs

    def get_interceptor(self, **kwargs):
        kwargs = self.get_interceptor_class_kwargs(**kwargs)
        interceptor_class = self.get_interceptor_class()
        return interceptor_class(**kwargs)

    def initial(self, request, *args, **kwargs):
        self.interceptor = self.get_interceptor(
            user=request.user if request.user.is_authenticated else None
        )
        return super(HTTPInterceptorView, self).initial(request, *args, **kwargs)

    def build_response(self, request):
        response = self.interceptor.response_data()

        return Response(
            data=response.get('data'),
            status=response.get('status'),
            headers=response.get('headers')
        )

    def create_intercepted_file(self, intercepted_request, param, file):
        instance = InterceptedFile.objects.create(
            request=intercepted_request,
            parameter=param,
            filename=file.name,
            size=file.size
        )

        return instance

    def intercept(self, request, *args, **kwargs):
        """
        Intercepts all request to main URL and save it on database.
        """
        if self.interceptor.can_perform_creation():

            intercepted_request = InterceptedRequest.objects.create(
                path=self.interceptor.path,
                method=request.method,
                params=json.dumps(request.query_params),
                data=json.dumps(self.interceptor.data),
                metadata=json.dumps(self.interceptor.meta),
                headers=json.dumps(dict(request.headers)),
                content_type=self.interceptor.content_type,
                session=self.interceptor.session
            )

            self.create_intercepted_files(intercepted_request, self.interceptor.files)

            return self.build_response(intercepted_request)

        else:
            return Response(data={'error': 'Unauthorized'}, status=HTTP_401_UNAUTHORIZED)

    def create_intercepted_files(self, request, files):
        for key, file in files.items():
            self.create_intercepted_file(request, key, file)


class HTTPSessionInterceptorView(HTTPInterceptorView):

    interceptor_class = HttpSessionInterceptor

    def initial(self, request, *args, **kwargs):
        try:
            return super(HTTPSessionInterceptorView, self).initial(request, *args, **kwargs)
        except SessionNotFoundError:
            raise Response(status=HTTP_401_UNAUTHORIZED)

    def get_interceptor_class_kwargs(self, **kwargs):
        session_name = self.kwargs.pop('session_name', None)
        kwargs = super(HTTPSessionInterceptorView, self).get_interceptor_class_kwargs(**kwargs)
        kwargs.update({'session_name': session_name})
        return kwargs

    def perform_authentication(self, request):
        """
        Overrides if authentication will be performed or overrided after request sending, for example a token
        in the session to override user in the request.
        """
        user = self.interceptor.authenticate()
        if user is not None:
            request.user = user

    def create_intercepted_file(self, intercepted_request, param, file, session=None):
        instance = super(HTTPSessionInterceptorView, self).create_intercepted_file(
            intercepted_request,
            param,
            file
        )

        if session and session.saves_files:
            instance.file = file
            instance.save()

    def create_intercepted_files(self, request, files):
        for key, file in files.items():
            self.create_intercepted_file(request, key, file, session=self.interceptor.session)

    def build_response(self, request):
        response = self.interceptor.response_data()

        request.matched_response = response.get('mock')
        request.save()

        return Response(
            data=response.get('data'),
            status=response.get('status'),
            headers=response.get('headers')
        )
