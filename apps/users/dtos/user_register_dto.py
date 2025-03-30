from dataclasses import dataclass
from typing import Optional

@dataclass
class UserRegisterDTO:
    email: str
    password: str
    first_name: str
    last_name: str
    restaurant_id: Optional[int] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None
    
    def validate(self):
        errors = {}
        if not self.email:
            errors['email'] = 'Email is required'
        if not self.password or len(self.password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        if not self.first_name:
            errors['first_name'] = 'First name is required'
        return errors
