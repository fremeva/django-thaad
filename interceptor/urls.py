from django.urls import path, re_path

from interceptor.views import HTTPInterceptorView, HTTPSessionInterceptorView

app_name = 'interceptor'

urlpatterns = [
    re_path('interceptor/(.*)', HTTPInterceptorView.as_view()),
    re_path(r'(?P<session_name>[A-Za-z0-9]{1,20})/(.*)', HTTPSessionInterceptorView.as_view())
]
