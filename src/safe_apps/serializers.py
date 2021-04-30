from rest_framework import serializers

from .models import SafeApp, Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["url", "name"]


class SafeAppsResponseSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer()

    class Meta:
        model = SafeApp
        fields = ["url", "name", "icon_url", "description", "networks", "provider"]
