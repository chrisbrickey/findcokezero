
from django.urls import re_path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'retailers', views.RetailerViewSet, basename='retailer') # added basename to allow custom get_queryset method
router.register(r'sodas', views.SodaViewSet)

urlpatterns = [
    re_path(r'^retailers/(?P<pk>[0-9]+)/sodas/$', views.sodas_by_retailer),
    re_path(r'^sodas/(?P<pk>[0-9]+)/retailers/$', views.retailers_by_sodas),
    re_path(r'^', include(router.urls)),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
