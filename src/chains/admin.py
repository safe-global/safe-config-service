# SPDX-License-Identifier: FSL-1.1-MIT
from typing import Any

from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms import BaseInlineFormSet, ModelForm

from .models import Chain, Feature, GasPrice, Service, Wallet


class WalletInlineFormSet(BaseInlineFormSet[Model, Model, ModelForm[Model]]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:
            default_wallets = list(Wallet.objects.filter(enable_by_default=True))
            self.initial = [{"wallet": wallet.id} for wallet in default_wallets]
            self.extra = len(default_wallets)


class GasPriceInline(admin.TabularInline[Model, Model]):
    model = GasPrice
    extra = 0
    verbose_name_plural = "Gas prices set for this chain"


class FeatureChainInlineForm(forms.ModelForm[Model]):
    class Meta:
        model = Feature.chains.through
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        per_chain = Feature.objects.filter(
            scope=Feature.Scope.PER_CHAIN
        ).order_by("key")
        for field in self.fields.values():
            if getattr(getattr(field, "queryset", None), "model", None) == Feature:
                field.queryset = per_chain
                break


class FeatureInline(admin.TabularInline[Model, Model]):
    model = Feature.chains.through
    form = FeatureChainInlineForm
    extra = 0
    verbose_name_plural = "Features enabled for this chain"


class WalletInline(admin.TabularInline[Model, Model]):
    model = Wallet.chains.through
    formset = WalletInlineFormSet
    extra = 0
    verbose_name_plural = "Wallets enabled for this chain"


class FeatureServiceInline(admin.TabularInline[Model, Model]):
    model = Feature.services.through
    extra = 0
    verbose_name_plural = "Features enabled for this service"


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin[Chain]):
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
    inlines = [FeatureInline, GasPriceInline, WalletInline]

    def formfield_for_foreignkey(
        self, db_field: Any, request: Any, **kwargs: Any
    ) -> Any:
        if db_field.name == "feature" and db_field.related_model == Feature:
            kwargs["queryset"] = Feature.objects.filter(
                scope=Feature.Scope.PER_CHAIN
            ).order_by("key")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(
        self,
        request: Any,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> Any:
        extra_context = extra_context or {}
        extra_context["global_features"] = Feature.objects.filter(
            scope=Feature.Scope.GLOBAL
        ).order_by("key")
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self,
        request: Any,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> Any:
        extra_context = extra_context or {}
        extra_context["global_features"] = Feature.objects.filter(
            scope=Feature.Scope.GLOBAL
        ).order_by("key")
        return super().add_view(request, form_url, extra_context)


@admin.register(GasPrice)
class GasPriceAdmin(admin.ModelAdmin[GasPrice]):
    list_display = (
        "chain_id",
        "oracle_uri",
        "fixed_wei_value",
        "rank",
    )
    search_fields = ("chain_id", "oracle_uri")
    ordering = ("rank",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin[Wallet]):
    list_display = ("key", "enable_by_default")
    list_editable = ("enable_by_default",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin[Service]):
    list_display = ("key", "name", "description")
    search_fields = ("key", "name")
    ordering = ("name",)
    inlines = [FeatureServiceInline]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin[Feature]):
    list_display = ("key", "scope", "description")
    list_editable = ("scope",)
    list_filter = ("scope", "services")
    fieldsets = (
        (None, {"fields": ("key", "description")}),
        (
            "Scope Configuration",
            {
                "fields": ("scope", "chains", "services"),
                "description": "Configure which chains and services have access to this feature.",
            },
        ),
    )

    class Media:
        js = ("admin/chains/feature_admin.js",)
