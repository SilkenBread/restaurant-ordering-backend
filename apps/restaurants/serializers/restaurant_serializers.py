from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from django.utils.translation import gettext_lazy as _
from datetime import datetime

@extend_schema_serializer(
    component_name="Restaurant",
    examples=[]
)
class RestaurantDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField()
    address = serializers.CharField()
    rating = serializers.FloatField()
    status = serializers.CharField()
    category = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(
        required=False,
        format="%Y-%m-%d %H:%M:%S",
        input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"]
    )
    updated_at = serializers.DateTimeField(
        required=False,
        format="%Y-%m-%d %H:%M:%S",
        input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"]
    )

    def validate_name(self, value):
        """Validación del nombre"""
        if not value or len(value) > 255:
            raise serializers.ValidationError(_("El nombre es requerido y debe tener máximo 255 caracteres"))
        return value
    
    def validate_rating(self, value):
        """Validación del rating"""
        if value < 0 or value > 5:
            raise serializers.ValidationError(_("El rating debe estar entre 0.0 y 5.0"))
        return value

class RestaurantCreateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField()
    rating = serializers.FloatField(min_value=0, max_value=5)
    status = serializers.CharField()
    category = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    is_active = serializers.BooleanField(default=True)

class RestaurantUpdateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(required=False)
    rating = serializers.FloatField(min_value=0, max_value=5, required=False)
    status = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    is_active = serializers.BooleanField(required=False)
