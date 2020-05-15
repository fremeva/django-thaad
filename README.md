# Django Thaad (interceptor)


Django thaad is a library that allows project to intercept all request in and endpoint
and save crutial information to inspect the payload in request, also you can create
mock responses to send back to the requester and create Fake APIs.

### How to use

Add interceptor app in your settings:

    INSTALLED_APPS = (
        #...
        'interceptor',
        #...
      )

Add interceptor urls in your main urls.py:

    urlpatterns = [
        #...
        path('', include('interceptor.urls', namespace='interceptor'))
        #...
    ]

