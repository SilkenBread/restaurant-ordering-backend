from typing import Optional, Dict, Any
from django.utils.translation import gettext_lazy as _

from apps.core.exceptions import ValidationException
from ..dtos.restaurant_dto import RestaurantDTO, RestaurantListDTO
from ..repositories.restaurant_repository import RestaurantRepository
from ..filters.restaurant_filters import RestaurantFilter
from rest_framework.exceptions import NotFound

class RestaurantService:
    """
    Servicio para manejar la lógica de negocio de restaurantes.
    
    Proporciona operaciones CRUD con validaciones y manejo de cache.
    """
    def __init__(self, repository: RestaurantRepository = None):
        self.repository = repository or RestaurantRepository()

    def get_restaurant(self, restaurant_id: int) -> Optional[RestaurantDTO]:
        """
        Obtiene un restaurante por ID.
        
        Args:
            restaurant_id (int): ID del restaurante
            
        Returns:
            Optional[RestaurantDTO]: DTO del restaurante o None si no existe
            
        Raises:
            NotFound: Si el restaurante no existe
        """
        restaurant = self.repository.get_by_id(restaurant_id)
        if not restaurant:
            raise NotFound(_("Restaurante no encontrado"))
        return self._to_dto(restaurant)
    
    def list_restaurants(self, filters: Optional[Dict[str, Any]] = None,
                        pagination: Optional[Dict[str, int]] = None) -> RestaurantListDTO:
        """
        Lista restaurantes con filtros y paginación.
        
        Args:
            filters (Optional[Dict[str, Any]]): Diccionario de filtros
            pagination (Optional[Dict[str, int]]): Configuración de paginación
            
        Returns:
            RestaurantListDTO: DTO con lista paginada de restaurantes
        """
        base_queryset = self.repository.get_all()

        # Aplicar filtros
        filter_set = RestaurantFilter(filters or {}, queryset=base_queryset)
        filtered_queryset = filter_set.qs

        # Paginación
        total = filtered_queryset.count()
        if pagination:
            page = pagination.get('page', 1)
            page_size = pagination.get('page_size', 10)
            filtered_queryset = filtered_queryset[(page-1)*page_size : page*page_size]
        
        items = [self._to_dto(item) for item in filtered_queryset]
        
        return RestaurantListDTO(
            items=items,
            total=total,
            page=pagination.get('page', 1) if pagination else 1,
            page_size=pagination.get('page_size', 10) if pagination else 10
        )
    
    def create_restaurant(self, restaurant_data: RestaurantDTO) -> RestaurantDTO:
        """
        Crea un nuevo restaurante.
        
        Args:
            restaurant_data (RestaurantDTO): Datos del restaurante a crear
            
        Returns:
            RestaurantDTO: DTO del restaurante creado
            
        Raises:
            ValidationException: Si los datos no son válidos
        """
        self._validate_restaurant_data(restaurant_data)
        restaurant = self._to_model(restaurant_data)
        created = self.repository.create(restaurant)
        return self._to_dto(created)
    
    def update_restaurant(self, restaurant_id: int, 
                        restaurant_data: RestaurantDTO) -> RestaurantDTO:
        """
        Actualiza un restaurante existente.
        
        Args:
            restaurant_id (int): ID del restaurante a actualizar
            restaurant_data (RestaurantDTO): Datos actualizados
            
        Returns:
            RestaurantDTO: DTO del restaurante actualizado
            
        Raises:
            NotFound: Si el restaurante no existe
            ValidationException: Si los datos no son válidos
        """
        existing = self.repository.get_by_id(restaurant_id)
        if not existing:
            raise NotFound(_("Restaurante no encontrado"))
        
        self._validate_restaurant_data(restaurant_data)
        restaurant = self._to_model(restaurant_data)
        restaurant.id = restaurant_id
        updated = self.repository.update(restaurant)
        return self._to_dto(updated)
    
    def delete_restaurant(self, restaurant_id: int) -> bool:
        """
        Elimina un restaurante.
        
        Args:
            restaurant_id (int): ID del restaurante a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        return self.repository.delete(restaurant_id)
    
    def _validate_restaurant_data(self, data: RestaurantDTO):
        """
        Valida los datos del restaurante.
        
        Args:
            data (RestaurantDTO): Datos a validar
            
        Raises:
            ValidationException: Si los datos no son válidos
        """
        errors = {}
        
        if not data.name or len(data.name) > 255:
            errors['name'] = _("El nombre es requerido y debe tener máximo 255 caracteres")
        
        if not data.address:
            errors['address'] = _("La dirección es requerida")
        
        if data.rating < 0 or data.rating > 5:
            errors['rating'] = _("El rating debe estar entre 0.0 y 5.0")
        
        if not data.category:
            errors['category'] = _("La categoría es requerida")
        
        if errors:
            raise ValidationException(_("Datos de restaurante inválidos"), errors)
        
    def _to_dto(self, model) -> RestaurantDTO:
        """
        Convierte un modelo Restaurant a RestaurantDTO.
    
        Args:
            model: Instancia del modelo Restaurant
            
        Returns:
            RestaurantDTO: DTO con los datos del restaurante
        """
        return RestaurantDTO(
            id=model.id,
            name=model.name,
            address=model.address,
            rating=float(model.rating),
            status=model.status,
            category=model.category,
            latitude=float(model.latitude),
            longitude=float(model.longitude),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, dto: RestaurantDTO):
        """
        Convierte un DTO a modelo.
        """
        return self.repository.model_class(
            name=dto.name,
            address=dto.address,
            rating=dto.rating,
            status=dto.status,
            category=dto.category,
            latitude=dto.latitude,
            longitude=dto.longitude,
            is_active=dto.is_active
        )
