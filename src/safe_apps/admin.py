from django.contrib import admin

from .models import Provider, SafeApp


class ChainIdFilter(admin.SimpleListFilter):
    title = "Chains"
    parameter_name = "chain_ids"

    def lookups(self, request, model_admin):
        values = SafeApp.objects.values_list("chain_ids", flat=True)
        # lookups requires a tuple to be returned – (value, verbose value)
        chains = [(chain, chain) for chains in values for chain in chains]
        chains = sorted(set(chains))
        return chains

    def queryset(self, request, queryset):
        if value := self.value():
            queryset = queryset.filter(chain_ids__contains=[value])
        return queryset


@admin.register(SafeApp)
class SafeAppAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "chain_ids")
    list_filter = (ChainIdFilter,)
    search_fields = ("name", "url")
    ordering = ("name",)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
    ordering = ("name",)
