from django.db import models
from django.core.cache import cache
from typing import Dict, Any, Optional
from apps.core.repositories.django_repository import DjangoRepository
from ..models import User

class UserRepository(DjangoRepository[User]):
    def __init__(self):
        super().__init__(User)
        self.cache_timeout = 60 * 15  # 15 minutos

    def get_by_id(self, id: int) -> Optional[User]:
        cache_key = f'user_{id}'
        user = cache.get(cache_key)
        
        if not user:
            user = super().get_by_id(id)
            if user:
                cache.set(cache_key, user, self.cache_timeout)
        
        return user
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'users_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_all(filters)
            cache.set(cache_key, queryset, self.cache_timeout) 
        return queryset
        
    def create(self, entity: User) -> User:
        entity = super().create(entity)
        cache.delete_pattern('users_*')
        return entity
    
    def update(self, entity: User) -> User:
        existing = self.get_by_id(entity.id)
        if not existing:
            return None
        
        changed_fields = []
        for field in ['email', 'first_name', 'last_name', 'phone', 
                     'default_address', 'restaurant_id', 'is_active']:
            if getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
        
        if not changed_fields:
            return existing
        
        entity.save(update_fields=changed_fields + ['last_updated'])
        
        cache.delete(f'user_{entity.id}')
        cache.delete_pattern('users_*')
        return entity
    
    def delete(self, id: int) -> bool:
        # desactivate the user instead of deleting it
        user = self.get_by_id(id)
        if not user:
            return False
        user.is_active = False
        user.save(update_fields=['is_active'])
        # remove from cache
        cache.delete(f'user_{id}')
        cache.delete_pattern('users_*')
        return True
