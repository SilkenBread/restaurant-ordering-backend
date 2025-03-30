from dataclasses import dataclass

@dataclass
class UserLogoutDTO:
    refresh: str
    
    def validate(self):
        errors = {}
        if not self.refresh:
            errors['refresh'] = 'Token de refresco es requerido'
        return errors
