from rest_framework import serializers

from .models import SafeApp


class SafeAppsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafeApp
        fields = ['url', 'name', 'icon_url', 'description', 'networks']
