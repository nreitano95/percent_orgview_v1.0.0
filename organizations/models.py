from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Favorites(models.Model):
    ukey = models.CharField(max_length=150)
    ein = models.CharField(max_length=100)
    user = models.CharField(max_length=100)


class Favorites2(models.Model):
    ukey = models.CharField(max_length=150)
    ein = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
