from dataclasses import dataclass
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

@dataclass
class PasswordChangeDTO:
    """
    DTO para cambio de contraseña
    
    Attributes:
        old_password (str): Contraseña actual
        new_password (str): Nueva contraseña
        confirm_password (str): Confirmación de nueva contraseña
    """
    old_password: str
    new_password: str
    confirm_password: str

    def validate(self, user=None):
        errors = {}

        if not self.old_password:
            errors['old_password'] = ['La contraseña actual es obligatoria']
        
        if not self.new_password:
            errors['new_password'] = ['La nueva contraseña es obligatoria']
        elif self.new_password != self.confirm_password:
            errors['confirm_password'] = ['Las contraseñas no coinciden']
        
        # Validación de la nueva contraseña
        if self.new_password:
            try:
                validate_password(self.new_password, user=user)
            except ValidationError as e:
                errors['new_password'] = e.detail if isinstance(e, ValidationError) else e.messages

        if errors:
            raise ValidationError(errors)
