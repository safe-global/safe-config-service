from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('safe_apps.urls', namespace='v1')),
    path('admin/', admin.site.urls),
]
