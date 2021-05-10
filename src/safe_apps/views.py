from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView

from .models import SafeApp
from .serializers import SafeAppsResponseSerializer


class SafeAppsListView(ListAPIView):
    serializer_class = SafeAppsResponseSerializer

    @method_decorator(cache_page(60 * 10, cache="safe-apps"))  # Cache 10 minutes
    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        queryset = SafeApp.objects.all()

        network_id = self.request.query_params.get("network_id")
        if network_id is not None and network_id.isdigit():
            queryset = queryset.filter(networks__contains=[network_id])

        return queryset
