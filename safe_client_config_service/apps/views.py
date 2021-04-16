from rest_framework.generics import ListAPIView

from .models import SafeApp
from .serializers import SafeAppsResponseSerializer


class SafeAppsListView(ListAPIView):
    queryset = SafeApp.objects.all()
    serializer_class = SafeAppsResponseSerializer
