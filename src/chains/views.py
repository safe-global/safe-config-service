from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from .models import Chain
from .serializers import ChainSerializer


class ChainsListView(ListAPIView):
    serializer_class = ChainSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.max_limit = 10
    pagination_class.default_limit = 10

    def get_queryset(self):
        return Chain.objects.all()
