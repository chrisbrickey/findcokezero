from django.contrib import admin
from django.urls import path, include

from inventory import urls as inventory_urls

from . import views

urlpatterns = [
    path('api/', include(inventory_urls)),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), # landing page
]