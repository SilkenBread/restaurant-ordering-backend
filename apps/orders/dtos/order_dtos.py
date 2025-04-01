from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class OrderItemDTO:
    menu_item_id: int
    quantity: int
    subtotal: float
    is_active: bool = True
    id: Optional[int] = None
    order_id: Optional[int] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class OrderDTO:
    customer_id: int
    restaurant_id: int
    total_amount: float
    status: str
    is_active: bool = True
    id: Optional[int] = None
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order_items: Optional[List[OrderItemDTO]] = None


@dataclass
class OrderCreateDTO:
    customer_id: int
    restaurant_id: int
    total_amount: float
    items: List[Dict[str, Any]]
    is_active: bool = True
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None


@dataclass
class OrderUpdateDTO:
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    is_active: Optional[bool] = None
