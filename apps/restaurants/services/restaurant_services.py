from rest_framework.exceptions import NotFound
from typing import Optional, Dict, Any, Union
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.core.exceptions import ValidationException
from ..models import Restaurant
from ..serializers.restaurant_serializers import RestaurantCreateDTOSerializer, RestaurantDTOSerializer, RestaurantUpdateDTOSerializer
from ..dtos.restaurant_dto import RestaurantCreateDTO, RestaurantDTO, RestaurantUpdateDTO
from ..repositories.restaurant_repository import RestaurantRepository
from ..filters.restaurant_filters import RestaurantFilter

class RestaurantService:
    def __init__(self, repository: RestaurantRepository = None):
        self.repository = repository or RestaurantRepository()

    def get_restaurant(self, restaurant_id: int) -> Optional[RestaurantDTO]:
        restaurant = self.repository.get_by_id(restaurant_id)
        if not restaurant:
            raise NotFound(_("Restaurante no encontrado"))
        return self._to_dto(restaurant)
    
    def list_restaurants(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        base_queryset = self.repository.get_all()

        # Aplicar filtros
        filter_set = RestaurantFilter(filters or {}, queryset=base_queryset)
        filtered_queryset = filter_set.qs

        return filtered_queryset.order_by('-created_at') 

    def create_restaurant(self, restaurant_data: RestaurantCreateDTO) -> Dict:
        serializer = RestaurantCreateDTOSerializer(data=restaurant_data.__dict__)
        serializer.is_valid(raise_exception=True)
        
        restaurant = self._to_model(restaurant_data)
        created = self.repository.create(restaurant)
        
        return RestaurantDTOSerializer(self._to_dto(created)).data
        
    def update_restaurant(self, restaurant_id: int, restaurant_data: RestaurantUpdateDTO) -> Dict:
        existing = self.repository.get_by_id(restaurant_id)
        if not existing:
            raise NotFound(_("Restaurante no encontrado"))
        
        serializer = RestaurantUpdateDTOSerializer(data=restaurant_data.__dict__)
        serializer.is_valid(raise_exception=True)
        
        # Actualizar campos
        for field, value in restaurant_data.__dict__.items():
            if value is not None:
                setattr(existing, field, value)
        
        updated = self.repository.update(existing)
        return RestaurantDTOSerializer(self._to_dto(updated)).data
    
    def delete_restaurant(self, restaurant_id: int) -> bool:
        return self.repository.delete(restaurant_id)
    
    def _validate_restaurant_data(self, data: RestaurantDTO):
        if not data.name or len(data.name) > 255:
            raise ValidationException(_("Nombre inválido"), 
                                    {"name": _("El nombre es requerido y debe tener máximo 255 caracteres")})
        
        if not data.address:
            raise ValidationException(_("Dirección inválida"), 
                                    {"address": _("La dirección es requerida")})
        
        if data.rating < 0 or data.rating > 5:
            raise ValidationException(_("Rating inválido"), 
                                    {"rating": _("El rating debe estar entre 0.0 y 5.0")})
        
        if not data.category:
            raise ValidationException(_("Categoría inválida"), 
                                    {"category": _("La categoría es requerida")})
        
    def _to_dto(self, model) -> RestaurantDTO:
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
    
    def _to_model(self, dto: Union[RestaurantCreateDTO, RestaurantUpdateDTO, RestaurantDTO]) -> Restaurant:
        model = self.repository.model_class()
        
        if isinstance(dto, RestaurantDTO):
            model.id = dto.id
            model.created_at = dto.created_at
            model.updated_at = dto.updated_at
        
        for field in ['name', 'address', 'rating', 'status', 
                    'category', 'latitude', 'longitude', 'is_active']:
            value = getattr(dto, field, None)
            if value is not None:
                setattr(model, field, value)
        
        return model
