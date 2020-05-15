from django.urls import path, re_path

from interceptor.views import InterceptorView

app_name = 'interceptor'

urlpatterns = [
    re_path('interceptor/(.*)', InterceptorView.as_view()),
    re_path(r'(?P<session_name>[A-Za-z0-9]{1,20})/(.*)', InterceptorView.as_view())
]
