from apps.core.repositories.django_repository import DjangoRepository
from typing import Optional, Dict, Any
from django.db import models, transaction
from django.core.cache import cache
from ..models import MenuItem


class MenuItemRepository(DjangoRepository[MenuItem]):
    def __init__(self):
        super().__init__(MenuItem)
        self.cache_timeout = 60 * 10  # 10 minutos
    
    def get_by_id(self, id: int) -> Optional[MenuItem]:
        cache_key = f'menu_item_{id}'
        menu_item = cache.get(cache_key)
        
        if not menu_item:
            menu_item = MenuItem.objects.select_related('restaurant').filter(id=id).first()
            if menu_item:
                cache.set(cache_key, menu_item, self.cache_timeout)
        
        return menu_item
    
    def get_by_restaurant_id(self, restaurant_id: int) -> models.QuerySet:
        """Obtener todos los ítems de menú de un restaurante específico"""
        cache_key = f'menu_items_restaurant_{restaurant_id}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = MenuItem.objects.filter(restaurant_id=restaurant_id, is_active=True)
            cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        # Construir clave de caché basada en filtros
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'menu_items_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            # Optimizar consulta con select_related
            queryset = MenuItem.objects.select_related('restaurant').all()
            
            # Aplicar filtros si existen
            if filters:
                queryset = super().apply_filters(queryset, filters)
                
            cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
    
    @transaction.atomic
    def create(self, entity: MenuItem) -> MenuItem:
        entity.save()
        
        cache.delete_pattern('menu_items_*')
        cache.delete_pattern(f'menu_items_restaurant_{entity.restaurant_id}')
    
        return entity
    
    @transaction.atomic
    def update(self, entity: MenuItem) -> MenuItem:
        existing = self.get_by_id(entity.id)
        if not existing:
            return None
        
        # campos que cambiaron
        changed_fields = []
        for field in ['name', 'description', 'price', 'preparation_time', 
                     'category', 'is_active', 'is_available', 'image']:
            if getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
        
        if not changed_fields:
            return existing
        
        # actualizar
        entity.save(update_fields=changed_fields + ['updated_at'])
        
        # invalidar cache
        cache.delete(f'menu_item_{entity.id}')
        cache.delete_pattern('menu_items_*')
        cache.delete_pattern(f'menu_items_restaurant_{entity.restaurant_id}')
        
        return entity
    
    @transaction.atomic
    def delete(self, id: int) -> bool:
        try:
            item = self.get_by_id(id)
            if not item:
                return False
            
            restaurant_id = item.restaurant_id

            item.is_active = False
            item.save(update_fields=['is_active', 'updated_at'])
            
            # Invalidar caché
            cache.delete(f'menu_item_{id}')
            cache.delete_pattern('menu_items_*')
            cache.delete_pattern(f'menu_items_restaurant_{restaurant_id}')
            
            return True
        except MenuItem.DoesNotExist:
            return False
