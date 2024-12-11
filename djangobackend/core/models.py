from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    settings = models.JSONField(default=dict)
    uid = models.CharField(max_length=255, unique=True)