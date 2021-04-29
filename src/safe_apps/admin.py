from django.contrib import admin

from .models import SafeApp, Provider

models = [SafeApp, Provider]
admin.site.register(models)
