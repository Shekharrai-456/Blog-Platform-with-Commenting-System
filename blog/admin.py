from django.contrib import admin
from .models import Category, Tag, Post, Comment

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
admin.site.register(Category, CategoryAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
admin.site.register(Tag, TagAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at", "category")
    search_fields = ("title", "content", "author__username")
    filter_horizontal = ("tags",)
admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("content", "author__username", "post__title")
    list_filter = ("created_at",)
admin.site.register(Comment, CommentAdmin)
