from typing import Any, Union

from django.db.models import Q, QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .models import SafeApp
from .serializers import SafeAppsResponseSerializer


def parse_boolean_query_param(value: Union[bool, str, int]) -> bool:
    return value in (True, "True", "true", "1", 1)


class SafeAppsListView(ListAPIView):  # type: ignore[type-arg]
    serializer_class = SafeAppsResponseSerializer
    pagination_class = None

    _swagger_chain_id_param = openapi.Parameter(
        "chainId",
        openapi.IN_QUERY,
        description="Used to filter Safe Apps that are available on `chainId`",
        type=openapi.TYPE_INTEGER,
    )
    _swagger_client_url_param = openapi.Parameter(
        "clientUrl",
        openapi.IN_QUERY,
        description="Used to filter Safe Apps that are available on `clientUrl`",
        type=openapi.TYPE_STRING,
    )
    _swagger_url_param = openapi.Parameter(
        "url",
        openapi.IN_QUERY,
        description="Filter Safe Apps available from `url`. `url` needs to be an exact match",
        type=openapi.TYPE_STRING,
    )

    _swagger_only_listed_param = openapi.Parameter(
        "onlyListed",
        openapi.IN_QUERY,
        description="If true, only listed/visible Safe Apps will be included. Else, all Safe Apps will be included",
        type=openapi.TYPE_BOOLEAN,
        default=False,
    )

    @method_decorator(cache_page(60 * 10, cache="safe-apps"))  # Cache 10 minutes
    @swagger_auto_schema(
        manual_parameters=[
            _swagger_chain_id_param,
            _swagger_client_url_param,
            _swagger_url_param,
            _swagger_only_listed_param,
        ]
    )  # type: ignore[misc]
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Returns a collection of Safe Apps (across different chains).
        Each Safe App can optionally include the information about the `Provider`
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[SafeApp]:
        only_listed = parse_boolean_query_param(
            self.request.query_params.get("onlyListed", False)
        )
        if only_listed:
            queryset = SafeApp.objects.filter(visible=True)
        else:
            queryset = SafeApp.objects.all()

        chain_id = self.request.query_params.get("chainId")
        if chain_id is not None and chain_id.isdigit():
            queryset = queryset.filter(chain_ids__contains=[chain_id])

        client_url = self.request.query_params.get("clientUrl")
        if client_url and "\0" not in client_url:
            queryset = queryset.filter(
                Q(exclusive_clients__url=client_url) | Q(exclusive_clients__isnull=True)
            )

        url = self.request.query_params.get("url")
        if url and "\0" not in url:
            queryset = queryset.filter(url=url)

        return queryset
