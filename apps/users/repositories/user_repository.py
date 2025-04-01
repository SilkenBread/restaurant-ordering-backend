from apps.core.repositories.django_repository import DjangoRepository
from typing import Dict, Any, Optional
from django.db import models, transaction
from django.core.cache import cache
from apps.users.models import User


class UserRepository(DjangoRepository[User]):
    def __init__(self):
        super().__init__(User)
        self.cache_timeout = 60 * 15  # 15 minutos
    
    def get_by_id(self, id: int) -> Optional[User]:
        cache_key = f'user_{id}'
        user = cache.get(cache_key)
        
        if not user:
            user = User.objects.select_related('restaurant').filter(id=id).first()
            if user:
                cache.set(cache_key, user, self.cache_timeout)
        
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        cache_key = f'user_email_{email}'
        user = cache.get(cache_key)
        
        if not user:
            user = User.objects.select_related('restaurant').filter(email=email).first()
            if user:
                cache.set(cache_key, user, self.cache_timeout)
        
        return user
    
    def get_by_restaurant_id(self, restaurant_id: int) -> models.QuerySet:
        """Obtener todos los usuarios de un restaurante específico"""
        cache_key = f'users_restaurant_{restaurant_id}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = User.objects.filter(restaurant_id=restaurant_id, is_active=True)
            cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        # Construir clave de caché basada en filtros
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'users_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            # Optimizar consulta con select_related
            queryset = User.objects.select_related('restaurant').all()
            
            # Aplicar filtros si existen
            if filters:
                queryset = super().apply_filters(queryset, filters)
                
            cache.set(cache_key, queryset, self.cache_timeout)
        
        return queryset
    
    @transaction.atomic
    def create(self, entity: User) -> User:
        # Si se proporciona contraseña sin cifrar, usar set_password
        password = getattr(entity, '_password', None)
        if password:
            entity.set_password(password)
            delattr(entity, '_password')
            
        entity.save()
        
        # Invalidar caché
        cache.delete_pattern('users_*')
        if entity.restaurant_id:
            cache.delete_pattern(f'users_restaurant_{entity.restaurant_id}')
    
        return entity
    
    @transaction.atomic
    def update(self, entity: User) -> User:
        existing = self.get_by_id(entity.id)
        if not existing:
            return None
        
        # Campos que cambiaron
        changed_fields = []
        for field in ['email', 'first_name', 'last_name', 'phone', 
                    'default_address', 'restaurant_id', 'is_staff', 
                    'is_superuser', 'is_active']:
            if hasattr(entity, field) and getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
                # Actualizar el valor
                setattr(existing, field, getattr(entity, field))
        
        # Manejar la contraseña especialmente
        password = getattr(entity, '_password', None)
        if password:
            existing.set_password(password)
        
        if not changed_fields and not password:
            return existing
        
        # Actualizar
        if changed_fields:
            existing.save(update_fields=changed_fields + ['last_updated'])
        elif password:
            existing.save(update_fields=['password', 'last_updated'])
        
        # Invalidar caché
        cache.delete(f'user_{entity.id}')
        cache.delete(f'user_email_{entity.email}')
        cache.delete_pattern('users_*')
        if entity.restaurant_id:
            cache.delete_pattern(f'users_restaurant_{entity.restaurant_id}')
        
        return existing
    
    @transaction.atomic
    def delete(self, id: int) -> bool:
        try:
            user = self.get_by_id(id)
            if not user:
                return False
            
            restaurant_id = user.restaurant_id

            # Desactivar en lugar de eliminar
            user.is_active = False
            user.save(update_fields=['is_active', 'last_updated'])
            
            # Invalidar caché
            cache.delete(f'user_{id}')
            cache.delete(f'user_email_{user.email}')
            cache.delete_pattern('users_*')
            if restaurant_id:
                cache.delete_pattern(f'users_restaurant_{restaurant_id}')
            
            return True
        except User.DoesNotExist:
            return False
