from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Client, Provider, SafeApp


class ProviderSerializer(serializers.ModelSerializer[Provider]):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class ClientSerializer(serializers.Serializer[Client]):
    @staticmethod
    def to_representation(instance: Client) -> str:
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


class SafeAppsResponseSerializer(serializers.ModelSerializer[SafeApp]):
    id = serializers.IntegerField(source="app_id")
    provider = ProviderSerializer()
    access_control = serializers.SerializerMethodField()

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
        ]

    @swagger_serializer_method(serializer_or_field=DomainAllowlistAccessControlPolicySerializer)  # type: ignore[misc]
    def get_access_control(self, instance: SafeApp) -> ReturnDict:
        if (
            instance.get_access_control_type()
            == SafeApp.AccessControlPolicy.DOMAIN_ALLOWLIST
        ):
            return DomainAllowlistAccessControlPolicySerializer(instance).data
        return NoRestrictionsAccessControlPolicySerializer(instance).data
