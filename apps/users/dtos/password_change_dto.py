# users/dtos/password_change_dto.py
from dataclasses import dataclass

@dataclass
class PasswordChangeDTO:
    current_password: str
    new_password: str
    confirm_password: str
    
    def validate(self, user) -> dict:
        errors = {}
        
        if not user.check_password(self.current_password):
            errors['current_password'] = 'Contraseña actual incorrecta'
        
        if len(self.new_password) < 8:
            errors['new_password'] = 'La nueva contraseña debe tener al menos 8 caracteres'
            
        if self.new_password != self.confirm_password:
            errors['confirm_password'] = 'Las contraseñas no coinciden'        
        return errors
