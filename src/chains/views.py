from django.db.models import query
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
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["relevance", "name"]
    ordering = [
        "relevance",
        "name",
    ]

    def get_queryset(self):
        queryset = Chain.objects.all()
        short_name = self.request.query_params.get("shortName")

        if short_name is not None:
            queryset = queryset.filter(short_name=short_name)
        return queryset


class ChainsDetailView(RetrieveAPIView):
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()


class ChainsDetailViewByShortName(RetrieveAPIView):
    lookup_field = "short_name"
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()
