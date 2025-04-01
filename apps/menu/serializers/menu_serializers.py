from rest_framework import serializers
from django.utils.translation import gettext as _


class MenuItemDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = serializers.IntegerField()
    category = serializers.CharField(max_length=100)
    restaurant_id = serializers.IntegerField()
    is_active = serializers.BooleanField(default=True)
    is_available = serializers.BooleanField(default=True)
    image = serializers.ImageField(required=False, allow_null=True)
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
        if not value or len(value) > 255:
            raise serializers.ValidationError(_("El nombre es requerido y debe tener máximo 255 caracteres"))
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("El precio debe ser mayor a cero"))
        return value
    
    def validate_preparation_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("El tiempo de preparación debe ser mayor a cero"))
        return value


class MenuItemCreateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    preparation_time = serializers.IntegerField(min_value=1)
    category = serializers.CharField(max_length=100)
    restaurant_id = serializers.IntegerField()
    is_active = serializers.BooleanField(default=True)
    is_available = serializers.BooleanField(default=True)
    image = serializers.ImageField(required=False, allow_null=True)


class MenuItemUpdateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False, allow_null=True)
    preparation_time = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    category = serializers.CharField(max_length=100, required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    is_available = serializers.BooleanField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    
    def validate_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(_("El precio debe ser mayor a cero"))
        return value
    
    def validate_preparation_time(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(_("El tiempo de preparación debe ser mayor a cero"))
        return value
