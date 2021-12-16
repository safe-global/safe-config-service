from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Provider, SafeApp, Client


class ProviderSerializer(serializers.ModelSerializer[Provider]):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class ClientSerializer(serializers.Serializer[Client]):
    @staticmethod
    def to_representation(instance: Client) -> str:
        return instance.url


class AccessControlPolicySerializer(serializers.Serializer[SafeApp]):
    type = serializers.CharField(source="access_control_type")
    data = ClientSerializer(source="access_control_sources", many=True)


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

    @staticmethod
    @swagger_serializer_method(serializer_or_field=AccessControlPolicySerializer)  # type: ignore[misc]
    def get_access_control(obj: SafeApp) -> ReturnDict:
        return AccessControlPolicySerializer(obj).data
