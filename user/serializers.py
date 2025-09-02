from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Username already exists."
        )]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Email already registered."
        )]
    )
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
