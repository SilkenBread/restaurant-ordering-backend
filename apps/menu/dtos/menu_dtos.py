from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MenuItemDTO:
    name: str
    description: str
    price: float
    preparation_time: int
    category: str
    restaurant_id: int
    is_active: bool = True
    is_available: bool = True
    id: Optional[int] = None
    image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MenuItemCreateDTO:
    name: str
    description: str
    price: float
    preparation_time: int
    category: str
    restaurant_id: int
    is_active: bool = True
    is_available: bool = True
    image: Optional[str] = None


@dataclass
class MenuItemUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    preparation_time: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None
    image: Optional[str] = None
