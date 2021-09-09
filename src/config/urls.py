from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config import settings

schema_view = get_schema_view(
    validators=["flex", "ssv"],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns_v1 = [
    path("about/", include("about.urls", namespace="about")),
    path("safe-apps/", include("safe_apps.urls", namespace="safe-apps")),
    path("chains/", include("chains.urls", namespace="chains")),
]

urlpatterns = [
    path("api/v1/", include((urlpatterns_v1, "v1"), namespace="v1")),
    path("admin/", admin.site.urls),
    path("check/", lambda request: HttpResponse("Ok"), name="check"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
