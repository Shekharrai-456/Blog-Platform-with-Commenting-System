from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorRole

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]  # authors only
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]  # owner/admin
        return [IsAuthenticatedOrReadOnly()]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]  # authors only
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]


class PostViewSet(viewsets.ModelViewSet):
    """
    - Anyone can list/read posts
    - Only role='author' can create posts
    - Only the post owner can update/delete
    - Search: title, content, category name, tags name, author username
    - Filter: category, tags, status, author__username, created_at (gte/lte/date)
      Examples:
        ?category=1
        ?tags=2        (exact tag id)
        ?status=P
        ?author__username=alice
        ?created_at__date=2025-08-20
        ?created_at__gte=2025-08-01&created_at__lte=2025-08-20
    - Ordering: ?ordering=-created_at or ?ordering=title
    """
    queryset = Post.objects.select_related("author", "category").prefetch_related("tags").all().order_by("-created_at")
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    # Let global DRF filter backends handle it;
    # just declare fields here:
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "category__name", "tags__name", "author__username"]
    ordering_fields = ["created_at", "title"]

    # Enable django-filter lookups via settings' DEFAULT_FILTER_BACKENDS
    # by declaring filterset_fields as a dict with lookups:
    from django_filters.rest_framework import DjangoFilterBackend
    filter_backends += [DjangoFilterBackend]  # add DF backend too
    filterset_fields = {
        "category": ["exact"],
        "tags": ["exact"],            # tags=<tag_id>
        "status": ["exact"],          # P or D
        "author__username": ["exact", "icontains"],
        "created_at": ["date", "gte", "lte"],
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    - Anyone can list/read comments
    - Any authenticated user (reader/author) can create a comment
    - Only the comment owner can update/delete
    - Search: content, author username
    - Filter: post, author__username, created_at
    - Ordering: created_at
    """
    queryset = Comment.objects.select_related("post", "author").all().order_by("-created_at")
    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content", "author__username"]
    ordering_fields = ["created_at"]

    from django_filters.rest_framework import DjangoFilterBackend
    filter_backends += [DjangoFilterBackend]
    filterset_fields = {
        "post": ["exact"],
        "author__username": ["exact", "icontains"],
        "created_at": ["date", "gte", "lte"],
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
