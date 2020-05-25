from rest_framework.routers import DefaultRouter

from interceptor.api.viewsets import InterceptedRequestModelListViewset, InterceptorSessionViewset

app_name = 'interceptor.api'

router = DefaultRouter()

router.register('request', InterceptedRequestModelListViewset)
router.register('session', InterceptorSessionViewset)

urlpatterns = router.urls
