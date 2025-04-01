# apps/users/dtos/user_dtos.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserDTO:
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    default_address: Optional[str]
    restaurant_id: Optional[int]
    is_staff: bool
    is_superuser: bool
    is_active: bool
    id: Optional[int] = None
    date_joined: Optional[datetime] = None
    last_updated: Optional[datetime] = None


@dataclass
class UserCreateDTO:
    email: str
    first_name: str
    last_name: str
    password: str
    phone: Optional[str] = None
    default_address: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_staff: bool = False
    is_superuser: bool = False
    is_active: bool = True


@dataclass
class UserUpdateDTO:
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
