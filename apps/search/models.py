from django.db import models


class Item(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    url = models.CharField(max_length=1024)
    domain = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    keywords = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024)
    verified = models.BooleanField()
    update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item'
        ordering = ['-update']
