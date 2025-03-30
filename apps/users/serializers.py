from rest_framework import serializers

from .dtos.user_response_dto import UserResponseDTO
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'default_address', 'is_active', 'restaurant_id'
            ]
        read_only_fields = ['id', 'email', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'is_active': {'required': False},
            'restaurant_id': {'required': False}
        }

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'phone', 'default_address', 'restaurant_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'email': {'required': True},
            'first_name': {'required': True}
        }

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name',
            'phone', 'default_address', 'is_active', 'restaurant_id'
        ]
        extra_kwargs = {
            'restaurant_id': {'required': False}
        }

class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False)
    default_address = serializers.CharField(required=False)
    access = serializers.CharField()
    refresh = serializers.CharField()
    
    def create(self, validated_data):
        return UserResponseDTO(**validated_data)

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)
