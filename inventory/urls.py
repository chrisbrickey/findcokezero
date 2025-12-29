
from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'retailers', views.RetailerViewSet, basename='retailer') # added basename to allow custom get_queryset method
router.register(r'sodas', views.SodaViewSet)

urlpatterns = [
    path('retailers/<int:pk>/sodas/', views.sodas_by_retailer),
    path('sodas/<int:pk>/retailers/', views.retailers_by_sodas),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
