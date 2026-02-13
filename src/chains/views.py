from typing import Any

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Chain, Feature, Service
from .serializers import ChainSerializer


class ChainsPagination(LimitOffsetPagination):
    default_limit = 40
    max_limit = 100


class ChainsListView(ListAPIView[Chain]):
    serializer_class = ChainSerializer
    pagination_class = ChainsPagination
    queryset = Chain.objects.filter(hidden=False).prefetch_related("feature_set")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["relevance", "name"]
    ordering = [
        "relevance",
        "name",
    ]


class ChainsDetailView(RetrieveAPIView[Chain]):
    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False).prefetch_related("feature_set")

    @swagger_auto_schema(
        operation_id="Get chain by id"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsDetailViewByShortName(RetrieveAPIView[Chain]):
    lookup_field = "short_name"
    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False).prefetch_related("feature_set")

    @swagger_auto_schema(
        operation_id="Get chain by shortName",
        operation_description="Warning: `shortNames` may contain characters that need to be URL encoded (i.e.: whitespaces)",  # noqa E501
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsListViewV2(ListAPIView[Chain]):
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
        return Chain.objects.filter(hidden=False).prefetch_related(
            Prefetch(
                "feature_set",
                queryset=Feature.objects.filter(
                    services=self.service, scope=Feature.Scope.PER_CHAIN
                ).order_by("key"),
            )
        )

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        service = getattr(self, "service", None)
        context["service"] = service
        if service:
            context["_service_global_features"] = list(
                Feature.objects.filter(
                    services=service, scope=Feature.Scope.GLOBAL
                ).order_by("key")
            )
        return context

    @swagger_auto_schema(
        operation_id="Get chains by service"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ChainsDetailViewV2(RetrieveAPIView[Chain]):
    """
    v2 endpoint that returns a single chain config filtered by service.

    Features are filtered based on:
    - Service assignment (feature must be assigned to the service)
    - Scope (GLOBAL features apply to all chains, PER_CHAIN only to selected chains)
    """

    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(hidden=False)

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        service = (
            get_object_or_404(Service, key=self.kwargs["service_key"])
            if self.kwargs.get("service_key")
            else None
        )
        context["service"] = service
        if service:
            context["_service_global_features"] = list(
                Feature.objects.filter(
                    services=service, scope=Feature.Scope.GLOBAL
                ).order_by("key")
            )
        return context

    @swagger_auto_schema(
        operation_id="Get chain by id for service"
    )  # type: ignore[untyped-decorator]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)
