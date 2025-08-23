# from django.contrib.auth import authenticate, get_user_model
# from rest_framework import viewsets, status
# from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser,IsAuthenticatedOrReadOnly
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from rest_framework.views import APIView 

# from .serializers import UserSerializer, RegisterSerializer
# from .permissions import IsSelfOrAdmin
from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated ,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from .permissions import IsSelfOrAdmin


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    # The main queryset for this ViewSet. 
    # This defines the set of users this ViewSet will operate on.
    queryset = User.objects.all()

    # Default serializer for this ViewSet (used for retrieve, update, delete)
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Returns a list of permission classes depending on the current action.
        This allows different endpoints to have different access rules.
        """
        if self.action in ["create", "login"]:
            # Anyone can register or login; no authentication required.
            return [AllowAny()]
        elif self.action == "list":
            # Viewing the list of all users requires authentication,
            # but allows read-only access if unauthenticated 
            return [IsAuthenticatedOrReadOnly()]
        elif self.action == "me":
            # Accessing current user's profile requires authentication
            return [IsAuthenticated()]
        else:
            # retrieve/update/delete of a specific user
            # Only the user themselves or an admin can perform these actions
            return [IsAuthenticated(), IsSelfOrAdmin()]

    @action(
        detail=False, 
        methods=["post"], 
        url_path="login", 
        permission_classes=[AllowAny]
    )
    
    
    def login(self, request):
        """
        Custom action for user login.
        - Expects 'username' and 'password' in request.data.
        - Authenticates the user.
        - Returns a token for API authentication.
        Logic:
        1. Get username & password from request.
        2. Authenticate user with Django's auth system.
        3. If authentication fails, return 401 error.
        4. If authentication succeeds, create/get token.
        5. Return the token and username in response.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Check credentials
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)

        # Generate or retrieve token for user
        token, _ = Token.objects.get_or_create(user=user)

        # Return token and username
        return Response({
            "token": token.key, 
            "username": user.username
        })

    @action(
        detail=False, 
        methods=["get", "put", "delete"], 
        url_path="me", 
        permission_classes=[IsAuthenticated]
    )
    
    
    def me(self, request):
        """
        Custom action for accessing/updating/deleting the currently logged user.
        Logic:
        - GET: Returns the serialized data of the current user.
        - PUT/PATCH: Updates the current user's profile with provided data.
        - DELETE: Deletes the currently logged-in user's account.
        """
        user = request.user

        if request.method == "GET":
            # Serialize and return the current user's details
            return Response(UserSerializer(user).data)

        elif request.method in ["PUT", "PATCH"]:
            # Partial update: allows updating only some fields
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)  # validate input
            serializer.save()  # save changes to DB
            return Response(serializer.data)

        elif request.method == "DELETE":
            # Delete current user from database
            user.delete()
            return Response({"detail": "Deleted"}, status=204)


