from typing import Any

from django.contrib import admin
from django.db.models import Model, QuerySet
from django.forms import ModelForm

from .models import Chain, Client, Feature, Provider, SafeApp, SocialProfile, Tag


class ChainFilter(admin.SimpleListFilter):
    title = "Chains"
    parameter_name = "chains"

    def lookups(self, request: Any, model_admin: Any) -> Any:
        return Chain.objects.values_list("id", "name")

    def queryset(self, request: Any, queryset: QuerySet[SafeApp]) -> QuerySet[SafeApp]:
        if value := self.value():
            queryset = queryset.filter(chains__id=value)
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


class SafeAppAdminForm(ModelForm):
    class Meta:
        model = SafeApp
        fields = "__all__"
        widgets = {
            "chains": admin.widgets.FilteredSelectMultiple("Chains", False),
        }


@admin.register(SafeApp)
class SafeAppAdmin(admin.ModelAdmin[SafeApp]):
    form = SafeAppAdminForm
    list_display = ("name", "url", "get_chains", "listed")
    list_filter = (ChainFilter,)
    search_fields = ("name", "url")
    ordering = ("name",)
    inlines = [
        TagInline,
        FeatureInline,
        SocialProfileInline,
    ]

    def get_chains(self, obj):
        return ", ".join([chain.name for chain in obj.chains.all()])

    get_chains.short_description = "Chains"


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


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ("chain_id", "name")
    search_fields = ("chain_id", "name")
