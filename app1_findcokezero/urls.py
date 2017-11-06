
from django.conf.urls import url, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'retailers', views.RetailerViewSet)
router.register(r'sodas', views.SodaViewSet)

urlpatterns = [
    url(r'^retailers/(?P<pk>[0-9]+)/sodas/$', views.sodas_by_retailer),
    url(r'^sodas/(?P<pk>[0-9]+)/retailers/$', views.retailers_by_sodas),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
