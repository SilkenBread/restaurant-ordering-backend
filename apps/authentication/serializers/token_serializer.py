from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

@extend_schema_serializer(
    examples=[
        {
            "access": "eyJhbGciOi...",
            "refresh": "eyJhbGciOi..."
        }
    ]
)
class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
