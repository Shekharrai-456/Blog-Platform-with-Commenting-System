from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsSelfOrAdmin

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    User API:
    - POST   /api/user/users/         → Register (anyone)
    - POST   /api/user/users/login/   → Login (get token)
    - GET    /api/user/users/me/      → Current logged-in user
    - GET    /api/user/users/{id}/    → Retrieve user (self or admin)
    - PUT    /api/user/users/{id}/    → Update user (self or admin)
    - DELETE /api/user/users/{id}/    → Delete user (self or admin)
    - GET    /api/user/users/         → List users (admin only)
    """
    queryset = User.objects.all()

    def get_permissions(self):
        """Different permissions depending on action"""
        if self.action in ["create", "login"]:
            return [AllowAny()]
        elif self.action == "me":
            return [IsAuthenticated()]
        elif self.action == "list":
            return [IsAuthenticated()]  # or stricter: IsAdminUser()
        else:  # retrieve/update/destroy
            return [IsAuthenticated(), IsSelfOrAdmin()]

    def get_serializer_class(self):
        """Use RegisterSerializer for create, otherwise normal serializer"""
        if self.action == "create":
            return RegisterSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Return profile of current logged-in user"""
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], url_path="login", permission_classes=[AllowAny])
    def login(self, request):
        """Login with username & password only, return token"""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
        })
        
    # def get_permissions(self):
    #     """Different permissions depending on action"""
    #     if self.action in ["create", "login"]:
    #         return [AllowAny()]
    #     elif self.action == "me":
    #         return [IsAuthenticated()]
    #     elif self.action == "list":
    #         return [IsAuthenticated()]  # or stricter: IsAdminUser()
    #     else:  # retrieve/update/destroy
    #         return [IsAuthenticated(), IsSelfOrAdmin()]

    # def get_serializer_class(self):
    #     """Use RegisterSerializer for create, otherwise normal serializer"""
    #     if self.action == "create":
    #         return RegisterSerializer
    #     return UserSerializer

    # @action(detail=False, methods=["get"], url_path="me")
    # def me(self, request):
    #     """Return profile of current logged-in user"""
    #     return Response(UserSerializer(request.user).data)

    # @action(detail=False, methods=["post"], url_path="login", permission_classes=[AllowAny])
    # def login(self, request):
    #     """
    #     Login with username & password only, return token
    #     """
    #     username = request.data.get("username")
    #     password = request.data.get("password")

    #     if not username or not password:
    #         return Response(
    #             {"detail": "Username and password are required."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     user = authenticate(username=username, password=password)
    #     if not user:
    #         return Response(
    #             {"detail": "Invalid username or password."},
    #             status=status.HTTP_401_UNAUTHORIZED,
    #         )

    #     token, _ = Token.objects.get_or_create(user=user)
    #     return Response({
    #         "token": token.key,
    #         "user_id": user.id,
    #         "username": user.username,
    #         "role": user.role,
    #     })