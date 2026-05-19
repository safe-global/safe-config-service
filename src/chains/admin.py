# SPDX-License-Identifier: FSL-1.1-MIT
from typing import Any

from django import forms
from django.contrib import admin
from django.db.models import Model, QuerySet
from django.forms import BaseInlineFormSet, ModelChoiceField, ModelForm
from django.http import HttpRequest, HttpResponse
from django.utils.html import mark_safe

from .models import Chain, Feature, GasPrice, Service, Token, Wallet


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
        if "feature" in self.fields:
            field = self.fields["feature"]
            if isinstance(field, ModelChoiceField):
                field.queryset = Feature.objects.filter(
                    scope=Feature.Scope.PER_CHAIN
                ).order_by("key")


class FeatureInline(admin.TabularInline[Model, Model]):
    model = Feature.chains.through
    form = FeatureChainInlineForm
    extra = 0
    verbose_name_plural = "Features enabled for this chain"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Model]:
        return (
            super()
            .get_queryset(request)
            .filter(feature__scope=Feature.Scope.PER_CHAIN)
        )


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

    def _get_global_features(self) -> QuerySet[Feature]:
        return Feature.objects.filter(
            scope=Feature.Scope.GLOBAL
        ).order_by("key")

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["global_features"] = self._get_global_features()
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self,
        request: HttpRequest,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["global_features"] = self._get_global_features()
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


class TokenChainListFilter(admin.SimpleListFilter):
    title = "chain"
    parameter_name = "chain"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin[Token]
    ) -> list[tuple[Any, str]]:
        return list(Chain.objects.values_list("id", "name").order_by("name"))

    def queryset(self, request: HttpRequest, queryset: QuerySet[Token]) -> QuerySet[Token]:
        if self.value():
            return queryset.filter(chains__id=self.value())
        return queryset


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin[Token]):
    list_display = ("address", "symbol", "enabled_chains")
    search_fields = ("address", "symbol")
    list_filter = (TokenChainListFilter,)
    filter_horizontal = ("chains",)
    fieldsets = (
        (None, {"fields": ("address", "symbol")}),
        (
            "Chains",
            {
                "fields": ("chains",),
                "description": (
                    "Select the chains where this token is accepted as fee payment. "
                    "To enable on all chains at once, save the token and use the "
                    "'Enable for all chains' action from the token list."
                ),
            },
        ),
    )
    actions = ["enable_for_all_chains"]

    @admin.display(description="Enabled chains")
    def enabled_chains(self, obj: Token) -> str:
        names = list(obj.chains.values_list("name", flat=True).order_by("name"))
        if not names:
            return mark_safe("<span style='color:#999'>Disabled</span>")
        return ", ".join(names)

    @admin.action(description="Enable for all chains")
    def enable_for_all_chains(
        self, request: HttpRequest, queryset: QuerySet[Token]
    ) -> None:
        all_chains = Chain.objects.all()
        for token in queryset:
            token.chains.set(all_chains)
        self.message_user(
            request, f"Enabled {queryset.count()} token(s) for all chains."
        )


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
