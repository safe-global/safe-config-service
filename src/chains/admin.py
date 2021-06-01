from django.contrib import admin

from .models import Chain


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    pass
