from django.contrib.postgres.fields import ArrayField
from django.db import models


class SafeApp(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=200)
    icon_url = models.URLField()
    description = models.CharField(max_length=200)
    networks = ArrayField(models.IntegerField())
