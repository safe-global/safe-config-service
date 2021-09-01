from django.contrib import admin

from .models import Chain, GasPrice


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "rpc_uri",
        "safe_apps_rpc_uri",
        "relevance",
    )
    search_fields = ("name", "id")
    ordering = (
        "relevance",
        "name",
    )


@admin.register(GasPrice)
class GasPrice(admin.ModelAdmin):
    list_display = (
        "chain_id",
        "oracle_uri",
        "fixed_wei_value",
        "rank",
    )
    search_fields = ("chain_id", "oracle_uri")
    ordering = ("rank",)
