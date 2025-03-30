from dataclasses import dataclass
from typing import Optional

@dataclass
class UserCreateDTO:
    email: str
    password: str
    first_name: str
    last_name: str
    restaurant_id: Optional[int] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None
    
    def validate(self) -> dict:
        errors = {}
        if not self.email:
            errors['email'] = 'El correo electrónico es requerido'
        if not self.password or len(self.password) < 8:
            errors['password'] = 'La contraseña debe tener al menos 8 caracteres'
        if not self.first_name:
            errors['first_name'] = 'El nombre es requerido'
        return errors
