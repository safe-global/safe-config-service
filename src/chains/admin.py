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


class FeatureAdminForm(forms.ModelForm[Feature]):
    class Meta:
        model = Feature
        fields = "__all__"

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean() or {}
        scope = cleaned_data.get("scope")
        chains = cleaned_data.get("chains")

        if scope == Feature.Scope.GLOBAL and chains:
            raise forms.ValidationError(
                {"chains": "Global scope features cannot have chains selected."}
            )
        return cleaned_data


class GasPriceInline(admin.TabularInline[Model, Model]):
    model = GasPrice
    extra = 0
    verbose_name_plural = "Gas prices set for this chain"


class FeatureInline(admin.TabularInline[Model, Model]):
    model = Feature.chains.through
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
    form = FeatureAdminForm
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
