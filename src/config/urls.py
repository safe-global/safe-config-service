from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('apps.urls', namespace='v1')),
    path('admin/', admin.site.urls),
]
