from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from apps.core.exceptions import ValidationException
from django.utils.translation import gettext_lazy as _

@dataclass
class UserDTO:
    email: str
    first_name: str
    last_name: str
    phone: str
    id: Optional[int] = None
    default_address: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_active: bool = True
    date_joined: Optional[datetime] = None
    last_updated: Optional[datetime] = None

@dataclass
class UserCreateDTO:
    email: str
    first_name: str
    last_name: str
    phone: str
    password: str
    default_address: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_active: bool = True

    def __post_init__(self):
        """"Validación inicial de campos requeridos"""
        missing_fields = []
        if self.email is None:
            missing_fields.append('email')
        if self.first_name is None:
            missing_fields.append('first_name')
        if self.last_name is None:
            missing_fields.append('last_name')
        if self.phone is None:
            missing_fields.append('phone')
        if self.password is None:
            missing_fields.append('password')

        if missing_fields:
            raise ValidationException(
                detail=_("Campos requeridos faltantes"),
                errors={field: [_("Este campo es requerido")] for field in missing_fields}
            )

@dataclass
class UserUpdateDTO:
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    default_address: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_active: Optional[bool] = None
