from typing import Any

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Chain, Service
from .serializers import ChainSerializer


class ChainsPagination(LimitOffsetPagination):
    default_limit = 40
    max_limit = 100


class ChainsListView(ListAPIView):  # type: ignore[type-arg]
    serializer_class = ChainSerializer
    pagination_class = ChainsPagination
    queryset = Chain.objects.filter(hidden=False)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["relevance", "name"]
    ordering = [
        "relevance",
        "name",
    ]


class ChainsDetailView(RetrieveAPIView):  # type: ignore[type-arg]
    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False)

    @swagger_auto_schema(
        operation_id="Get chain by id"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsDetailViewByShortName(RetrieveAPIView):  # type: ignore[type-arg]
    lookup_field = "short_name"
    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False)

    @swagger_auto_schema(
        operation_id="Get chain by shortName",
        operation_description="Warning: `shortNames` may contain characters that need to be URL encoded (i.e.: whitespaces)",  # noqa E501
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsListViewV2(ListAPIView):  # type: ignore[type-arg]
    """
    v2 endpoint that returns chain configs filtered by service.

    Features are filtered based on:
    - Service assignment (feature must be assigned to the service)
    - Scope (GLOBAL features apply to all chains, PER_CHAIN only to selected chains)
    """

    serializer_class = ChainSerializer
    pagination_class = ChainsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["relevance", "name"]
    ordering = ["relevance", "name"]

    def get_queryset(self) -> Any:
        self.service = get_object_or_404(Service, key=self.kwargs["service_key"])
        return Chain.objects.filter(hidden=False)

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["service"] = getattr(self, "service", None)
        return context

    @swagger_auto_schema(
        operation_id="Get chains by service"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsDetailViewV2(RetrieveAPIView):  # type: ignore[type-arg]
    """
    v2 endpoint that returns a single chain config filtered by service.

    Features are filtered based on:
    - Service assignment (feature must be assigned to the service)
    - Scope (GLOBAL features apply to all chains, PER_CHAIN only to selected chains)
    """

    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False)

    def get_queryset(self) -> Any:
        self.service = get_object_or_404(Service, key=self.kwargs["service_key"])
        return Chain.objects.filter(hidden=False)

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context["service"] = getattr(self, "service", None)
        return context

    @swagger_auto_schema(
        operation_id="Get chain by id for service"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)
