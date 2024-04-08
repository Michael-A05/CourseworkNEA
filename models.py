from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class CustomUser(AbstractUser):
    pass

    # Can add additional fields here

    def __str__(self):
        return self.username


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Choice(models.Model):
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chosen = models.BooleanField(default=False)

