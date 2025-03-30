from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class RestaurantDTO:
    name: str
    address: str
    rating: float
    status: str
    category: str
    latitude: float
    longitude: float
    is_active: bool = True  
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class RestaurantCreateDTO:
    name: str
    address: str
    rating: float
    status: str
    category: str
    latitude: float
    longitude: float
    is_active: bool = True

@dataclass
class RestaurantUpdateDTO:
    name: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    status: Optional[str] = None
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None
