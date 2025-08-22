from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    # Specify the fields to display in the list view of the admin
    list_display = ("username", "role", "is_staff", "is_active")
    
    # Add filters to the admin list view for easier navigation
    list_filter = ("role", "is_staff", "is_active")
