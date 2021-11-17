from rest_framework import serializers

from .models import Provider, SafeApp


class ProviderSerializer(serializers.ModelSerializer[Provider]):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class SafeAppsResponseSerializer(serializers.ModelSerializer[SafeApp]):
    id = serializers.IntegerField(source="app_id")
    provider = ProviderSerializer()

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
        ]
