from django.db import models

# Create your models here.

class Event(models.Model):
    Description = models.CharField(max_length=1000)
    SendAt = models.DateTimeField()
