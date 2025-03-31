from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class MenuItemDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = serializers.IntegerField()
    category = serializers.CharField()
    restaurant_id = serializers.IntegerField()
    is_active = serializers.BooleanField(default=True)
    is_available = serializers.BooleanField(default=True)
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
    image = serializers.ImageField(required=False, allow_null=True)
    
    def validate_name(self, value):
        if not value or len(value) > 255:
            raise serializers.ValidationError(_("El nombre es requerido y debe tener máximo 255 caracteres"))
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(_("El precio no puede ser negativo"))
        return value
    
    def validate_preparation_time(self, value):
        if value < 0:
            raise serializers.ValidationError(_("El tiempo de preparación no puede ser negativo"))
        return value

class MenuItemCreateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        error_messages={'required': _('Este campo es requerido')}
    )
    description = serializers.CharField(
        error_messages={'required': _('Este campo es requerido')}
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        error_messages={
            'required': _('Este campo es requerido'),
            'invalid': _('Ingrese un precio válido')
        }
    )
    preparation_time = serializers.IntegerField(
        error_messages={
            'required': _('Este campo es requerido'),
            'invalid': _('Ingrese un tiempo de preparación válido')
        }
    )
    category = serializers.CharField(
        max_length=100,
        error_messages={'required': _('Este campo es requerido')}
    )
    restaurant_id = serializers.IntegerField(
        error_messages={
            'required': _('Este campo es requerido'),
            'invalid': _('Ingrese un ID de restaurante válido')
        }
    )
    is_active = serializers.BooleanField(default=True)
    is_available = serializers.BooleanField(default=True)
    image = serializers.ImageField(required=False, allow_null=True)
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(_("El precio no puede ser negativo"))
        return value
    
    def validate_preparation_time(self, value):
        if value < 0:
            raise serializers.ValidationError(_("El tiempo de preparación no puede ser negativo"))
        return value

class MenuItemUpdateDTOSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        required=False,
        error_messages={
            'max_length': _('El nombre debe tener máximo 255 caracteres')
        }
    )
    description = serializers.CharField(
        required=False,
        error_messages={
            'invalid': _('Ingrese una descripción válida')
        }
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        error_messages={
            'invalid': _('Ingrese un precio válido')
        }
    )
    preparation_time = serializers.IntegerField(
        required=False,
        error_messages={
            'invalid': _('Ingrese un tiempo de preparación válido')
        }
    )
    category = serializers.CharField(
        max_length=100,
        required=False,
        error_messages={
            'max_length': _('La categoría debe tener máximo 100 caracteres')
        }
    )
    restaurant_id = serializers.IntegerField(
        required=False,
        error_messages={
            'invalid': _('Ingrese un ID de restaurante válido')
        }
    )
    is_active = serializers.BooleanField(required=False)
    is_available = serializers.BooleanField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(_("El precio no puede ser negativo"))
        return value
    
    def validate_preparation_time(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(_("El tiempo de preparación no puede ser negativo"))
        return value
    
    def validate(self, data):
        """
        Validación adicional a nivel de objeto:
        - Verifica que al menos un campo sea proporcionado
        """
        if not data:
            raise serializers.ValidationError({
                "non_field_errors": [_("Debe proporcionar al menos un campo para actualizar")]
            })
        
        return data
