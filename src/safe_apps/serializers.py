from rest_framework import serializers

from .models import Provider, SafeApp


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class SafeAppsResponseSerializer(serializers.ModelSerializer):
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
