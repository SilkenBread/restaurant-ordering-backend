from dataclasses import dataclass
from typing import Optional

@dataclass
class UserFilterDTO:
    """DTO para filtrar usuarios"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    restaurant_id: Optional[int] = None
    search: Optional[str] = None

    def validate(self) -> dict:
        errors = {}
        if self.is_active is not None and not isinstance(self.is_active, bool):
            errors['is_active'] = 'El estado de actividad debe ser un valor booleano'
        if self.restaurant_id is not None and not isinstance(self.restaurant_id, int):
            errors['restaurant_id'] = 'El ID del restaurante debe ser un número entero'
        return errors
