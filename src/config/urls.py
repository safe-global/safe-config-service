# SPDX-License-Identifier: FSL-1.1-MIT
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import URLPattern, URLResolver, include, path, re_path
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config import settings


def _schema_urlpatterns(
    patterns: list[URLPattern | URLResolver], prefix: str, name_prefix: str
) -> list[URLPattern | URLResolver]:
    schema_view = get_schema_view(
        validators=["flex", "ssv"],
        public=True,
        permission_classes=(permissions.AllowAny,),
        patterns=patterns,
    )
    return [
        re_path(
            rf"^{prefix}swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name=f"{name_prefix}schema-json",
        ),
        re_path(
            rf"^{prefix}$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name=f"{name_prefix}schema-swagger-ui",
        ),
    ]


urlpatterns_v1 = [
    path("about/", include("about.urls", namespace="about")),
    path("safe-apps/", include("safe_apps.urls", namespace="safe-apps")),
    path("chains/", include("chains.urls", namespace="chains")),
]

urlpatterns_v2 = [
    path("chains/", include("chains.urls_v2", namespace="chains")),
]

api_urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1/", include((urlpatterns_v1, "v1"), namespace="v1")),
    path("api/v2/", include((urlpatterns_v2, "v2"), namespace="v2")),
]

# For in-cluster consumers only: the public ingress does not route /internal.
internal_api_urlpatterns: list[URLPattern | URLResolver] = [
    path("internal/", include((api_urlpatterns, "internal"), namespace="internal")),
]

urlpatterns = (
    api_urlpatterns
    + internal_api_urlpatterns
    + _schema_urlpatterns(internal_api_urlpatterns, "internal/", "internal-")
    + [
        path("admin/", admin.site.urls),
        path("check/", lambda request: HttpResponse("Ok"), name="check"),
    ]
    + _schema_urlpatterns(api_urlpatterns, "", "")
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
