from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from apps.core.exceptions import ValidationException

@dataclass
class MenuItemDTO:
    name: str
    description: str
    price: Decimal
    preparation_time: int
    category: str
    restaurant_id: int
    id: Optional[int] = None
    is_active: bool = True
    is_available: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image: Optional[str] = None

@dataclass
class MenuItemCreateDTO:
    name: str
    description: str
    price: Decimal
    preparation_time: int
    category: str
    restaurant_id: int
    is_active: bool = True
    is_available: bool = True
    image: Optional[Any] = None
    
    def __post_init__(self):
        """Validación inicial de campos requeridos"""
        missing_fields = []
        if self.name is None:
            missing_fields.append('name')
        if self.description is None:
            missing_fields.append('description')
        if self.price is None:
            missing_fields.append('price')
        if self.preparation_time is None:
            missing_fields.append('preparation_time')
        if self.category is None:
            missing_fields.append('category')
        if self.restaurant_id is None:
            missing_fields.append('restaurant_id')
        
        if missing_fields:
            raise ValidationException(
                detail=_("Campos requeridos faltantes"),
                errors={field: [_("Este campo es requerido")] for field in missing_fields}
            )
        
        # Validaciones adicionales
        if self.price is not None and self.price < 0:
            raise ValidationException(
                detail=_("El precio debe ser mayor o igual a cero"),
                errors={'price': [_("El precio no puede ser negativo")]}
            )
        
        if self.preparation_time is not None and self.preparation_time < 0:
            raise ValidationException(
                detail=_("El tiempo de preparación debe ser mayor o igual a cero"),
                errors={'preparation_time': [_("El tiempo de preparación no puede ser negativo")]}
            )

@dataclass
class MenuItemUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    preparation_time: Optional[int] = None
    category: Optional[str] = None
    restaurant_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None
    image: Optional[Any] = None
    
    def __post_init__(self):
        """Validación de restricciones en los campos"""
        if self.price is not None and self.price < 0:
            raise ValidationException(
                detail=_("El precio debe ser mayor o igual a cero"),
                errors={'price': [_("El precio no puede ser negativo")]}
            )
        
        if self.preparation_time is not None and self.preparation_time < 0:
            raise ValidationException(
                detail=_("El tiempo de preparación debe ser mayor o igual a cero"),
                errors={'preparation_time': [_("El tiempo de preparación no puede ser negativo")]}
            )
