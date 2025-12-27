from django.urls import path, include
from app1_findcokezero import urls as app1_findcokezero_urls
from django.contrib import admin
from . import views

urlpatterns = [
    path('api/', include(app1_findcokezero_urls)),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), # landing page
]