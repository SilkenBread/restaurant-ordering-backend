from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from apps.core.dtos.base import ListDTO

@dataclass
class RestaurantDTO:
    """
    DTO para representar un restaurante.
    
    Attributes:
        id (Optional[int]): ID del restaurante
        name (str): Nombre del restaurante
        address (str): Dirección completa
        rating (float): Calificación de 0.0 a 5.0
        status (str): Estado del restaurante (open/closed/maintenance)
        category (str): Categoría del restaurante
        latitude (float): Coordenada de latitud
        longitude (float): Coordenada de longitud
        is_active (bool): Indica si el restaurante está activo
        created_at (Optional[datetime]): Fecha de creación
        updated_at (Optional[datetime]): Fecha de última actualización
    """
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
class RestaurantListDTO(ListDTO[RestaurantDTO]):
    """
    DTO para representar una lista paginada de restaurantes.
    
    Attributes:
        items (List[RestaurantDTO]): Lista de restaurantes
        total (int): Total de restaurantes sin paginación
        page (int): Página actual
        page_size (int): Tamaño de la página
    """
    pass
