from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ("author", "Author"),
        ("reader", "Reader"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="reader")

    def __str__(self):
        return f"{self.username} ({self.role})"
