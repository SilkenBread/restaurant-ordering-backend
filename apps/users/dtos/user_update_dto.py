from dataclasses import dataclass
from typing import Optional

@dataclass
class UserUpdateDTO:
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    restaurant_id: Optional[int] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None
    is_active: Optional[bool] = None
    
    def validate(self) -> dict:
        errors = {}
        if self.email and not self.email.strip():
            errors['email'] = 'El correo electrónico no puede estar vacío'
        return errors
