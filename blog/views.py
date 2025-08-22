from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorRole

# Create your views here.

"""
API endpoint for categories:
- List & retrieve: anyone
- Create: only authors
- Update/Delete: only owner or admin
- Search by category name
"""
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    
    def get_permissions(self):
        #Assign permissions based on action type
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]  # authors only
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]  # owner/admin
        return [IsAuthenticatedOrReadOnly()]

"""
API endpoint for tags:
- List & retrieve: anyone
- Create: only authors
- Update/Delete: only owner or admin
- Search by tag name
"""

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    
    def get_permissions(self):
        #Assign permissions based on action type
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly(), IsAuthorRole()]  # authors only
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]


"""
API endpoint for blog posts:
- List & retrieve: anyone
- Create: authors only
- Update/Delete: only owner
- Filter by category, tags, status, author, created_at
- Search by title, content, category name, tag name, author username
- Ordering by created_at or title
"""
class PostViewSet(viewsets.ModelViewSet):
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


"""
API endpoint for comments:
- List & retrieve: anyone
- Create: any authenticated user
- Update/Delete: only owner
- Filter by post, author, created_at
- Search by content or author username
- Ordering by created_at
"""
class CommentViewSet(viewsets.ModelViewSet):
    
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
