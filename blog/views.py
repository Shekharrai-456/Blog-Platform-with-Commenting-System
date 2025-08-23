from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorRole
from django_filters.rest_framework import DjangoFilterBackend


# CATEGORY VIEWSET

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog categories.
    Features:
    - List & retrieve: accessible to anyone.
    - Create: only authors can create new categories.
    - Update/Delete: only owner (or admin) can modify or delete.
    - Search by category name via DRF SearchFilter.
    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # default
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        """
        Dynamically assign permissions based on action:
        - 'create': user must be authenticated AND have author role
        - 'update', 'partial_update', 'destroy': user must be owner/admin
        - list/retrieve: read-only for everyone
        """
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]



# TAG VIEWSET

class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog tags.
    Features:
    - List & retrieve: accessible to anyone.
    - Create: only authors can create new tags.
    - Update/Delete: only owner (or admin) can modify or delete.
    - Search by tag name via DRF SearchFilter.
    """
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # default
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        """
        Dynamically assign permissions based on action:
        - 'create': only authors
        - 'update', 'partial_update', 'destroy': owner/admin
        - list/retrieve: read-only
        """
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]



# POST VIEWSET

class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog posts.
    Features:
    - List & retrieve: anyone.
    - Create: only authors.
    - Update/Delete: only post owner.
    - Filter by category, tags, status, author, created_at.
    - Search by title, content, category name, tag name, author username.
    - Ordering by created_at or title.
    """
    queryset = Post.objects.select_related("author", "category").prefetch_related("tags").all().order_by("-created_at")
    serializer_class = PostSerializer

    # DRF permissions based on action
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    # Search and ordering backends
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["title", "content", "category__name", "tags__name", "author__username"]
    ordering_fields = ["created_at", "title"]

    # Django-filter lookup fields for filtering in query params
    filterset_fields = {
        "category": ["exact"],
        "tags": ["exact"],            # filter by tag id
        "status": ["exact"],          # P (published) or D (draft)
        "author__username": ["exact", "icontains"],
        "created_at": ["date", "gte", "lte"],
    }

    def perform_create(self, serializer):
        """
        Automatically set the author of a post to the currently logged-in user.
        """
        serializer.save(author=self.request.user)



# COMMENT VIEWSET

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments on blog posts.
    Features:
    - List & retrieve: anyone.
    - Create: any authenticated user.
    - Update/Delete: only comment owner.
    - Filter by post, author, created_at.
    - Search by content or author username.
    - Ordering by created_at.
    """
    queryset = Comment.objects.select_related("post", "author").all().order_by("-created_at")
    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["content", "author__username"]
    ordering_fields = ["created_at"]

    # Django-filter lookup fields for filtering in query params
    filterset_fields = {
        "post": ["exact"],
        "author__username": ["exact", "icontains"],
        "created_at": ["date", "gte", "lte"],
    }

    def perform_create(self, serializer):
        """
        Automatically assign the currently logged-in user as the author of the comment.
        """
        serializer.save(author=self.request.user)
