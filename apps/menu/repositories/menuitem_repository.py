from typing import Optional, Dict, Any
from django.db import models, transaction
from django.core.cache import cache
from apps.core.repositories.django_repository import DjangoRepository
from apps.menu.models import MenuItem

class MenuItemRepository(DjangoRepository[MenuItem]):
    def __init__(self):
        super().__init__(MenuItem)
        self.cache_timeout = 60 * 15  # 15 minutos
    
    def get_by_id(self, id: int) -> Optional[MenuItem]:
        cache_key = f'menu_item_{id}'
        menu_item = cache.get(cache_key)
        
        if not menu_item:
            menu_item = super().get_by_id(id)
            if menu_item:
                cache.set(cache_key, menu_item, self.cache_timeout)
        
        return menu_item
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'menu_items_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_all(filters)
            cache.set(cache_key, queryset, self.cache_timeout) 
        
        return queryset
    
    def create(self, entity: MenuItem) -> MenuItem:
        entity = super().create(entity)
        # Invalidar cache que pueda contener listas de items
        cache.delete_pattern('menu_items_*')
        return entity
    
    def update(self, entity: MenuItem) -> MenuItem:
        existing = self.get_by_id(entity.id)
        if not existing:
            return None
        
        # Determinar que campos han cambiado
        changed_fields = []
        for field in ['name', 'description', 'price', 'preparation_time', 
                     'category', 'is_active', 'is_available', 'restaurant_id', 'image']:
            if getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
        
        if not changed_fields:
            return existing
        
        # Actualizar solo los campos que han cambiado
        entity.save(update_fields=changed_fields + ['updated_at'])
        
        # Invalidar caché
        cache.delete(f'menu_item_{entity.id}')
        cache.delete_pattern('menu_items_*')
        
        return entity
    
    def delete(self, id: int) -> bool:
        menu_item = self.get_by_id(id)
        if not menu_item:
            return False
        
        # En lugar de borrar físicamente, desactivamos el ítem
        menu_item.is_active = False
        menu_item.save(update_fields=['is_active', 'updated_at'])
        
        # Invalidar caché
        cache.delete(f'menu_item_{id}')
        cache.delete_pattern('menu_items_*')
        
        return True
    
    @transaction.atomic
    def hard_delete(self, id: int) -> bool:
        """Eliminación física del registro. Usar con precaución."""
        result = super().delete(id)
        if result:
            cache.delete(f'menu_item_{id}')
            cache.delete_pattern('menu_items_*')
        return result
