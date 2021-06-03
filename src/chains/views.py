from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination

from .models import Chain
from .serializers import ChainSerializer


class ChainsListView(ListAPIView):
    serializer_class = ChainSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.max_limit = 10
    pagination_class.default_limit = 10
    queryset = Chain.objects.all()


class ChainsDetailView(RetrieveAPIView):
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()
