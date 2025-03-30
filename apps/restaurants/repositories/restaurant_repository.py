from typing import Optional, Dict, Any
from django.core.cache import cache
from django.db import models
from apps.core.repositories.django_repository import DjangoRepository
from ..models import Restaurant

class RestaurantRepository(DjangoRepository[Restaurant]):
    def __init__(self):
        super().__init__(Restaurant)
        self.cache_timeout = 60 * 15  # 15 minutos

    def get_by_id(self, id: int) -> Optional[Restaurant]:
        cache_key = f'restaurant_{id}'
        restaurant = cache.get(cache_key)
        
        if not restaurant:
            restaurant = super().get_by_id(id)
            if restaurant:
                cache.set(cache_key, restaurant, self.cache_timeout)
        
        return restaurant
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'restaurants_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_all(filters)
            cache.set(cache_key, queryset, self.cache_timeout) 
        return queryset
        
    def create(self, entity: Restaurant) -> Restaurant:
        entity = super().create(entity)
        cache.delete_pattern('restaurants_*')
        return entity
    
    def update(self, entity: Restaurant) -> Restaurant:
        # Obtener el objeto existente para comparación
        existing = self.get_by_id(entity.id)
        if not existing:
            return None
        
        # Determinar qué campos realmente cambiaron
        changed_fields = []
        for field in ['name', 'address', 'rating', 'status', 
                    'category', 'latitude', 'longitude', 'is_active']:
            if getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
        
        if not changed_fields:
            return existing
        
        # Actualizar solo los campos que cambiaron
        entity.save(update_fields=changed_fields + ['updated_at'])
        
        # Invalidar caché
        cache.delete(f'restaurant_{entity.id}')
        cache.delete_pattern('restaurants_*')
        return entity
    
    def delete(self, id: int) -> bool:
        result = super().delete(id)
        if result:
            cache.delete_pattern(f'restaurant_{id}')
            cache.delete_pattern('restaurants_*')
        return result
