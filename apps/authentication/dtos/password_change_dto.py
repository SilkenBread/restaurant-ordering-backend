from dataclasses import dataclass
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from apps.core.exceptions import ValidationException

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
        
        # Validación básica de campos
        if not self.old_password:
            errors['old_password'] = [_('La contraseña actual es obligatoria')]
        
        if not self.new_password:
            errors['new_password'] = [_('La nueva contraseña es obligatoria')]
        elif self.new_password != self.confirm_password:
            errors['confirm_password'] = [_('Las contraseñas no coinciden')]
        
        # Validación de complejidad de contraseña
        if self.new_password and not errors.get('new_password'):
            try:
                validate_password(self.new_password, user=user)
            except ValidationError as e:
                errors['new_password'] = list(e.messages) if hasattr(e, 'messages') else [str(e)]
        
        if errors:
            raise ValidationException(
                detail=_("Error en validación de contraseña"),
                errors=errors
            )
