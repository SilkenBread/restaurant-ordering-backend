from dataclasses import dataclass
from typing import Optional
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from apps.core.exceptions import ValidationException

@dataclass
class PasswordChangeDTO:
    """
    DTO para cambio de contraseña
    """
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    confirm_password: Optional[str] = None

    def __post_init__(self):
        """Validación inicial de campos requeridos"""
        missing_fields = []
        if self.old_password is None:
            missing_fields.append('old_password')
        if self.new_password is None:
            missing_fields.append('new_password')
        if self.confirm_password is None:
            missing_fields.append('confirm_password')
        
        if missing_fields:
            raise ValidationException(
                detail=_("Campos requeridos faltantes"),
                errors={field: [_("Este campo es requerido")] for field in missing_fields}
            )
        
    def validate(self, user=None):
        errors = {}
        
        # Validación de coincidencia de contraseñas
        if self.new_password != self.confirm_password:
            errors['confirm_password'] = [_('Las contraseñas no coinciden')]
        
        # Validación de complejidad de contraseña
        if self.new_password:
            try:
                validate_password(self.new_password, user=user)
            except ValidationError as e:
                errors['new_password'] = list(e.messages) if hasattr(e, 'messages') else [str(e)]
        
        if errors:
            raise ValidationException(
                detail=_("Error en validación de contraseña"),
                errors=errors
            )
