from typing import Any, List

from django import forms
from django.contrib import admin
from django.db.models import Model, QuerySet

from chains.models import Chain

from .models import Client, Feature, Provider, SafeApp, SocialProfile, Tag


# Custom form for SafeApp to use Chain model in a multi-select field
class SafeAppForm(forms.ModelForm[SafeApp]):
    chain_ids = forms.ModelMultipleChoiceField(
        queryset=Chain.objects.all(), widget=forms.SelectMultiple, required=True
    )

    class Meta:
        model = SafeApp
        fields = "__all__"

    def clean_chain_ids(self) -> List[int]:
        """
        Override clean_chain_ids to store the selected Chain IDs as a list of integers.
        """
        chain_ids = self.cleaned_data["chain_ids"]
        return [chain.id for chain in chain_ids]


class ChainIdFilter(admin.SimpleListFilter):
    title = "Chains"
    parameter_name = "chain_ids"

    def lookups(self, request: Any, model_admin: Any) -> Any:
        values = SafeApp.objects.values_list("chain_ids", flat=True)
        # lookups requires a tuple to be returned – (value, verbose value)
        chains = [(chain, chain) for chains in values for chain in chains]
        chains = sorted(set(chains))
        return chains

    def queryset(self, request: Any, queryset: QuerySet[SafeApp]) -> QuerySet[SafeApp]:
        if value := self.value():
            queryset = queryset.filter(chain_ids__contains=[value])
        return queryset


class FeatureInline(admin.TabularInline[Model, Model]):
    model = Feature.safe_apps.through
    extra = 0
    verbose_name_plural = "Features set for this Safe App"


class TagInline(admin.TabularInline[Model, Model]):
    model = Tag.safe_apps.through
    extra = 0
    verbose_name_plural = "Tags set for this Safe App"


class SocialProfileInline(admin.TabularInline[Model, Model]):
    model = SocialProfile
    extra = 0
    verbose_name_plural = "Social profiles set for this Safe App"


@admin.register(SafeApp)
class SafeAppAdmin(admin.ModelAdmin[SafeApp]):
    form = SafeAppForm  # Use the custom form for SafeApp
    list_display = ("name", "url", "chain_ids", "listed")
    list_filter = (ChainIdFilter,)
    search_fields = ("name", "url")
    ordering = ("name",)
    inlines = [
        TagInline,
        FeatureInline,
        SocialProfileInline,
    ]


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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin[Tag]):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin[Feature]):
    list_display = ("key",)
    search_fields = ("key",)
    ordering = ("key",)


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin[SocialProfile]):
    list_display = ("safe_app", "url", "platform")
    search_fields = ("name", "url")
    ordering = ("platform",)
