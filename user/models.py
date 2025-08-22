from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
        
    # Define choices for the user role
    ROLE_CHOICES = (
        ("author", "Author"),
        ("reader", "Reader"),
    )
    
    # Add a 'role' field to the User model with specified choices and a default value
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="reader")

    def __str__(self):
        return f"{self.username} ({self.role})"
