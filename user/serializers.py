from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ["username", "password", "role"]  
        extra_kwargs = {
            "role": {"default": "reader"}  # Default role is reader
        }

    def create(self, validated_data):
        # Extract role, defaulting to 'reader'
        role = validated_data.get("role", "reader")
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            role=role,
        )
        Token.objects.create(user=user)  # Create token on registration
        return user
