from django.contrib import admin

from .models import Chain


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rpc_url")
    search_fields = ("name", "id")
    ordering = ("id",)
