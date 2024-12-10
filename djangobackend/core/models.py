from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    settings = models.JSONField(default=dict)
    uid = models.CharField(max_length=255, unique=True)