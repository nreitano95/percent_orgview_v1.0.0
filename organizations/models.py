from django.db import models


class User_Favorites(models.Model):
    ukey = models.CharField(max_length=150)
    ein = models.CharField(max_length=100)
    user = models.CharField(max_length=100)