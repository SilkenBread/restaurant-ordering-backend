from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class UserDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    default_address = serializers.CharField(required=False, allow_null=True)
    restaurant_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    date_joined = serializers.DateTimeField(
        required=False,
        format="%Y-%m-%d %H:%M:%S",
        input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"]
    )
    last_updated = serializers.DateTimeField(
        required=False,
        format="%Y-%m-%d %H:%M:%S",
        input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"]
    )

    def validate_email(self, value):
        if not value or len(value) > 255:
            raise serializers.ValidationError(_("El email es requerido y debe tener máximo 255 caracteres"))
        return value
    
    def validate_first_name(self, value):
        if not value or len(value) > 100:
            raise serializers.ValidationError(_("El nombre es requerido y debe tener máximo 100 caracteres"))
        return value
    
    def validate_last_name(self, value):
        if not value or len(value) > 100:
            raise serializers.ValidationError(_("El apellido es requerido y debe tener máximo 100 caracteres"))
        return value

class UserCreateDTOSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=255,
        error_messages={
            'required': _('Este campo es requerido'),
            'invalid': _('Ingrese un email válido')
        }
    )
    first_name = serializers.CharField(
        max_length=100,
        error_messages={'required': _('Este campo es requerido')}
    )
    last_name = serializers.CharField(
        max_length=100,
        error_messages={'required': _('Este campo es requerido')}
    )
    phone = serializers.CharField(
        max_length=20,
        error_messages={'required': _('Este campo es requerido')}
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={'required': _('Este campo es requerido')}
    )
    default_address = serializers.CharField(
        required=False,
        allow_null=True,
        error_messages={'blank': _('Este campo no puede estar vacío')}
    )
    restaurant_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={'invalid': _('Ingrese un ID de restaurante válido')}
    )
    is_active = serializers.BooleanField(default=True)

class UserUpdateDTOSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=255,
        required=False,
        error_messages={
            'invalid': _('Ingrese un email válido'),
            'max_length': _('El email debe tener máximo 255 caracteres')
        }
    )
    first_name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages={
            'max_length': _('El nombre debe tener máximo 100 caracteres')
        }
    )
    last_name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages={
            'max_length': _('El apellido debe tener máximo 100 caracteres')
        }
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        error_messages={
            'max_length': _('El teléfono debe tener máximo 20 caracteres')
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={
            'blank': _('La contraseña no puede estar vacía')
        }
    )
    default_address = serializers.CharField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid': _('Dirección no válida')
        }
    )
    restaurant_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid': _('ID de restaurante no válido')
        }
    )
    is_active = serializers.BooleanField(
        required=False,
        error_messages={
            'invalid': _('El estado activo debe ser verdadero o falso')
        }
    )

    def validate_email(self, value):
        if value and len(value) > 255:
            raise serializers.ValidationError(_("El email debe tener máximo 255 caracteres"))
        return value

    def validate_first_name(self, value):
        if value and len(value) > 100:
            raise serializers.ValidationError(_("El nombre debe tener máximo 100 caracteres"))
        return value

    def validate_last_name(self, value):
        if value and len(value) > 100:
            raise serializers.ValidationError(_("El apellido debe tener máximo 100 caracteres"))
        return value

    def validate_phone(self, value):
        if value and len(value) > 20:
            raise serializers.ValidationError(_("El teléfono debe tener máximo 20 caracteres"))
        return value
    
    def validate(self, data):
        """
        Validación adicional a nivel de objeto:
        - Verifica que al menos un campo sea proporcionado
        - Valida que la contraseña no esté vacía si se proporciona
        """
        if not data:
            raise serializers.ValidationError({
                "non_field_errors": ["Debe proporcionar al menos un campo para actualizar"]
            })
        
        if 'password' in data and not data['password']:
            raise serializers.ValidationError({
                'password': ["La contraseña no puede estar vacía"]
            })
        
        return data
