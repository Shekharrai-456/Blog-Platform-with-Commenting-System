from rest_framework import serializers
from .models import Category, Tag, Post, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "category", "category_name",
            "tags", "status", "created_at", "author"
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    post_title = serializers.ReadOnlyField(source="post.title")

    class Meta:
        model = Comment
        fields = ["id", "post", "post_title", "content", "created_at", "author"]
