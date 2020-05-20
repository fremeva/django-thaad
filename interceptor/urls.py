from django.conf.urls import url
from django.urls import path, re_path, include

from interceptor.api import API_VERSION
from interceptor.views import HTTPInterceptorView, HTTPSessionInterceptorView

app_name = 'interceptor'

urlpatterns = [
    url(f'api/{API_VERSION}/', include('interceptor.api.urls')),
    re_path('interceptor/(.*)', HTTPInterceptorView.as_view()),
    re_path(r's/(?P<session_name>[A-Za-z0-9]{1,20})/(.*)', HTTPSessionInterceptorView.as_view())  # Should remain last
]
