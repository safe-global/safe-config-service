from django.contrib.postgres.fields import ArrayField
from django.db import models


class Provider(models.Model):
    url = models.URLField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name} | {self.url}'


class SafeApp(models.Model):
    url = models.URLField(primary_key=True)
    name = models.CharField(max_length=200)
    icon_url = models.URLField()
    description = models.CharField(max_length=200)
    networks = ArrayField(models.IntegerField())
    provider = models.ForeignKey(Provider, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.name} | {self.url} | networks={self.networks}'
