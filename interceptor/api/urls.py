from rest_framework.routers import DefaultRouter

from interceptor.api.viewsets import InterceptedRequestModelListViewset

router = DefaultRouter()

router.register('request', InterceptedRequestModelListViewset)

urlpatterns = router.urls
