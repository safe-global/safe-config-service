from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

urlpatterns = [
    path("api/v1/", include("safe_apps.urls", namespace="v1")),
    path("admin/", admin.site.urls),
    re_path(r"^check/", lambda request: HttpResponse("Ok"), name="check"),
]
