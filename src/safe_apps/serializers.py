from typing import Any

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Client, Feature, Provider, SafeApp, SocialProfile, Tag


class ProviderSerializer(serializers.ModelSerializer[Provider]):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class ClientSerializer(serializers.Serializer[Client]):
    @staticmethod
    def to_representation(instance: Client) -> str:  # type: ignore[override]
        return instance.url


class DomainAllowlistAccessControlPolicySerializer(serializers.Serializer[SafeApp]):
    type = serializers.ReadOnlyField(
        default=SafeApp.AccessControlPolicy.DOMAIN_ALLOWLIST.value
    )
    value = ClientSerializer(source="exclusive_clients", many=True)


class NoRestrictionsAccessControlPolicySerializer(serializers.Serializer[SafeApp]):
    type = serializers.ReadOnlyField(
        default=SafeApp.AccessControlPolicy.NO_RESTRICTIONS.value
    )


class TagSerializer(serializers.ModelSerializer[Tag]):
    class Meta:
        fields = ["name"]
        model = Tag
        ref_name = "safe_apps.serializers.TagSerializer"

    def to_representation(self, instance: Tag) -> str:  # type: ignore[override]
        return instance.name


class FeatureSerializer(serializers.ModelSerializer[Feature]):
    class Meta:
        fields = ["key"]
        model = Feature
        ref_name = "safe_apps.serializers.FeatureSerializer"

    @staticmethod
    def to_representation(instance: Feature) -> str:  # type: ignore[override]
        return instance.key


class SocialProfileSerializer(serializers.ModelSerializer[SocialProfile]):
    class Meta:
        fields = ["platform", "url"]
        model = SocialProfile
        ref_name = "safe_apps.serializers.SocialProfileSerializer"

    platform = serializers.CharField()
    url = serializers.URLField()


class SafeAppsResponseSerializer(serializers.ModelSerializer[SafeApp]):
    id = serializers.IntegerField(source="app_id")
    icon_url = serializers.ImageField(use_url=True)
    provider = ProviderSerializer()
    access_control = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    social_profiles = serializers.SerializerMethodField()

    class Meta:
        model = SafeApp
        fields = [
            "id",
            "url",
            "name",
            "icon_url",
            "description",
            "chain_ids",
            "provider",
            "access_control",
            "tags",
            "features",
            "developer_website",
            "social_profiles",
            "featured",
        ]

    @swagger_serializer_method(serializer_or_field=DomainAllowlistAccessControlPolicySerializer)  # type: ignore[misc]
    def get_access_control(self, instance: SafeApp) -> ReturnDict[Any, Any]:
        if (
            instance.get_access_control_type()
            == SafeApp.AccessControlPolicy.DOMAIN_ALLOWLIST
        ):
            return DomainAllowlistAccessControlPolicySerializer(instance).data
        return NoRestrictionsAccessControlPolicySerializer(instance).data

    @swagger_serializer_method(serializer_or_field=TagSerializer)  # type: ignore[misc]
    def get_tags(self, instance: SafeApp) -> ReturnDict[Any, Any]:
        queryset = instance.tag_set.all().order_by("name")
        return TagSerializer(queryset, many=True).data

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)  # type: ignore[misc]
    def get_features(self, instance: SafeApp) -> ReturnDict[Any, Any]:
        features = instance.feature_set.all().order_by("key")
        return FeatureSerializer(features, many=True).data

    @swagger_serializer_method(serializer_or_field=SocialProfileSerializer)  # type: ignore[misc]
    def get_social_profiles(self, instance: SafeApp) -> ReturnDict[Any, Any]:
        profiles = instance.socialprofile_set.all().order_by("platform")
        return SocialProfileSerializer(profiles, many=True).data
