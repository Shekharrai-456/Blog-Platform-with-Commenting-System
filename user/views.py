from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Control access:
        - create & login: open to all
        - list: authenticated users
        - me: authenticated users
        - other actions: authenticated users only
        """
        if self.action in ["create", "login"]:
            return [AllowAny()]
        elif self.action in ["list", "me"]:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="login", permission_classes=[AllowAny])
    def login(self, request):
        """
        Login endpoint.
        Requires username & password.
        Returns auth token, username, and role.
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
            "role": user.role
        })

    @action(detail=False, methods=["get", "put", "delete"], url_path="me", permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Manage the current authenticated user.
        - GET: retrieve profile
        - PUT: update profile
        - DELETE: delete account
        """
        user = request.user

        if request.method == "GET":
            return Response(UserSerializer(user).data)

        elif request.method in ["PUT", "PATCH"]:
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            user.delete()
            return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
