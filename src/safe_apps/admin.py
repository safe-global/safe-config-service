from typing import Any

from django.contrib import admin
from django.db.models import QuerySet

from .models import Client, Provider, SafeApp


class ChainIdFilter(admin.SimpleListFilter):
    title = "Chains"
    parameter_name = "chain_ids"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        values = SafeApp.objects.values_list("chain_ids", flat=True)
        # lookups requires a tuple to be returned – (value, verbose value)
        chains = [(chain, chain) for chains in values for chain in chains]
        chains = sorted(set(chains))
        return chains

    def queryset(self, request: Any, queryset: QuerySet[SafeApp]) -> QuerySet[SafeApp]:
        if value := self.value():
            queryset = queryset.filter(chain_ids__contains=[value])
        return queryset


@admin.register(SafeApp)
class SafeAppAdmin(admin.ModelAdmin[SafeApp]):
    list_display = ("name", "url", "chain_ids", "visible")
    list_filter = (ChainIdFilter,)
    search_fields = ("name", "url")
    ordering = ("name",)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin[Provider]):
    list_display = ("name", "url")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin[Client]):
    list_display = ("url",)
    search_fields = ("url",)
    ordering = ("url",)
