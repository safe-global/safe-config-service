from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from .models import Chain
from .serializers import ChainSerializer


class ChainsListView(ListAPIView):
    serializer_class = ChainSerializer

    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        return Chain.objects.all()
