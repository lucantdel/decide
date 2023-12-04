from django.db import models
from django.utils import timezone

class CustomUser(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.username
