from django.db import models


class Configuration(models.Model):
    name = models.CharField(max_length=255, primary_key=True, null=False, blank=False)
    conf = models.TextField()
    custom_settings = models.TextField()
    interval = models.IntegerField(default=600)
    auto_run = models.BooleanField(default=False)

    class Meta:
        db_table = 'configuration'
        ordering = ['name']
