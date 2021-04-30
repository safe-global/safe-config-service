from django.contrib import admin

from .models import SafeApp, Provider


class NetworksFilter(admin.SimpleListFilter):
    title = "Networks"
    parameter_name = "networks"

    def lookups(self, request, model_admin):
        values = SafeApp.objects.values_list("networks", flat=True)
        # lookups requires a tuple to be returned – (value, verbose value)
        networks = [(network, network) for networks in values for network in networks]
        networks = sorted(set(networks))
        return networks

    def queryset(self, request, queryset):
        if value := self.value():
            queryset = queryset.filter(networks__contains=[value])
        return queryset


@admin.register(SafeApp)
class SafeAppAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "networks")
    list_filter = (NetworksFilter,)
    search_fields = ("name", "url")
    ordering = ("name",)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
    ordering = ("name",)
