from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from .models import SafeApp
from .serializers import SafeAppsResponseSerializer


class SafeAppsListView(ListAPIView):
    serializer_class = SafeAppsResponseSerializer

    _swagger_network_id_param = openapi.Parameter(
        "network_id",
        openapi.IN_QUERY,
        description="Used to filter Safe Apps that are available on `network_id`",
        type=openapi.TYPE_INTEGER,
    )

    @method_decorator(cache_page(60 * 10, cache="safe-apps"))  # Cache 10 minutes
    @swagger_auto_schema(manual_parameters=[_swagger_network_id_param])
    def get(self, request, *args, **kwargs):
        """
        Returns a collection of Safe Apps (across different networks).
        Each Safe App can optionally include the information about the `Provider`
        """
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        queryset = SafeApp.objects.all()

        network_id = self.request.query_params.get("network_id")
        if network_id is not None and network_id.isdigit():
            queryset = queryset.filter(networks__contains=[network_id])

        return queryset
