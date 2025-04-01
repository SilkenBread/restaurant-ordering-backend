from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class UserDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_null=True)
    default_address = serializers.CharField(required=False, allow_null=True)
    restaurant_id = serializers.IntegerField(required=False, allow_null=True)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
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
        if not value:
            raise serializers.ValidationError(_("El correo electrónico es requerido"))
        return value


class UserCreateDTOSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_null=True)
    default_address = serializers.CharField(required=False, allow_null=True)
    restaurant_id = serializers.IntegerField(required=False, allow_null=True)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    password = serializers.CharField(write_only=True)
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e))
        return value


class UserUpdateDTOSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_null=True)
    default_address = serializers.CharField(required=False, allow_null=True)
    restaurant_id = serializers.IntegerField(required=False, allow_null=True)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(list(e))
        return value


class BulkUserUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=True,
        help_text="Archivo CSV con los usuarios a crear. Formato: email;first_name;last_name;phone;password;...",
        error_messages={
            'required': _('Debe proporcionar un archivo CSV')
        }
    )
    
    def validate_file(self, value):
        """
        Validación del archivo CSV:
        - Verifica que el archivo sea un CSV
        - Verifica que el tamaño del archivo no exceda 1MB
        """
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError(_("El archivo debe ser CSV"))
        
        if value.size > 1024 * 1024:  # 1MB máximo
            raise serializers.ValidationError(_("El archivo es demasiado grande (máximo 1MB)"))
        
        return value
