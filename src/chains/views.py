from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination

from .models import Chain
from .serializers import ChainSerializer


class ChainsListView(ListAPIView):
    serializer_class = ChainSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.max_limit = 100
    pagination_class.default_limit = 10
    queryset = Chain.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["relevance", "name"]
    ordering = [
        "relevance",
        "name",
    ]


class ChainsDetailView(RetrieveAPIView):
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()
