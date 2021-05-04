from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("safe_apps.urls", namespace="v1")),
    path("admin/", admin.site.urls),
]
