from rest_framework.generics import ListAPIView

from .models import SafeApp
from .serializers import SafeAppsResponseSerializer


class SafeAppsListView(ListAPIView):
    serializer_class = SafeAppsResponseSerializer

    def get_queryset(self):
        queryset = SafeApp.objects.all()

        network_id = self.request.query_params.get("network_id")
        if network_id is not None and network_id.isdigit():
            queryset = queryset.filter(networks__contains=[network_id])

        return queryset
