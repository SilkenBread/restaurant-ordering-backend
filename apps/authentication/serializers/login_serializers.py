from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

@extend_schema_serializer(
    examples=[
        {
            "email": "admin@example.com",
            "password": "securepassword123"
        }
    ]
)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
