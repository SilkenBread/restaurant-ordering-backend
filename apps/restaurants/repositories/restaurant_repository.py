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
        """
        Obtiene un restaurante por ID
        
        Args:
            id (int): ID del restaurante
            
        Returns:
            Optional[Restaurant]: Instancia del modelo o None si no existe
        """
        cache_key = f'restaurant_{id}'
        restaurant = cache.get(cache_key)
        
        if not restaurant:
            restaurant = super().get_by_id(id)
            if restaurant:
                cache.set(cache_key, restaurant, self.cache_timeout)
        
        return restaurant
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        """
        Obtiene todos los restaurantes con posibilidad de filtrar
        
        Args:
            filters (Optional[Dict[str, Any]]): Diccionario de filtros
            
        Returns:
            models.QuerySet: QuerySet de restaurantes
        """
        cache_key = f'restaurants_all_{str(filters)}'
        
        # Obtener parámetros de filtro para reconstruir el queryset
        cached_params = cache.get(cache_key)
        
        if cached_params is None:
            # Si no hay cache, crear nuevo queryset
            queryset = super().get_all(filters)

            cache.set(cache_key, {
                'filters': filters,
                'model': self.model_class.__name__
            }, self.cache_timeout)
            return queryset
        else:
            # Reconstruir el queryset desde los parámetros
            queryset = self.model_class.objects.all()
            if cached_params['filters']:
                queryset = queryset.filter(**cached_params['filters'])
            return queryset
    
    def create(self, entity: Restaurant) -> Restaurant:
        """
        Crea un nuevo restaurante
        
        Args:
            entity (Restaurant): Instancia del modelo a crear
            
        Returns:
            Restaurant: Instancia creada
        """
        entity = super().create(entity)
        cache.delete_pattern('restaurants_*')
        return entity
    
    def update(self, entity: Restaurant) -> Restaurant:
        """
        Actualiza un restaurante
        
        Args:
            entity (Restaurant): Instancia del modelo a actualizar
            
        Returns:
            Restaurant: Instancia actualizada
        """
        entity.save(update_fields=[
            'name', 'address', 'rating', 'status', 
            'category', 'latitude', 'longitude', 'is_active'
        ])
        cache.delete_pattern(f'restaurant_{entity.id}')
        cache.delete_pattern('restaurants_*')
        return entity
    
    def delete(self, id: int) -> bool:
        """
        Elimina un restaurante
        
        Args:
            id (int): ID del restaurante a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        result = super().delete(id)
        if result:
            cache.delete_pattern(f'restaurant_{id}')
            cache.delete_pattern('restaurants_*')
        return result
