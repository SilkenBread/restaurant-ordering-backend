from typing import Optional, Dict, Any, List
from django.db import models, transaction
from django.core.cache import cache
from apps.core.repositories.django_repository import DjangoRepository
from ..models import Order, OrderItem
import json


class OrderRepository(DjangoRepository[Order]):
    def __init__(self):
        super().__init__(Order)
        self.cache_timeout = 60 * 5  # 5 minutos

    def get_by_id(self, id: int) -> Optional[Order]:
        cache_key = f'order_{id}'
        order = cache.get(cache_key)
        
        if not order:
            order = super().get_by_id(id)
            if order:
                order = Order.objects.select_related(
                    'customer', 'restaurant'
                ).prefetch_related(
                    'order_items', 'order_items__menu_item'
                ).get(id=id)
                cache.set(cache_key, order, self.cache_timeout)
        
        return order
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        filter_str = '_'.join(f"{k}:{v}" for k, v in sorted(filters.items())) if filters else "all"
        cache_key = f'orders_{filter_str}'
        
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Order.objects.select_related(
                'customer', 'restaurant'
            ).all()
            
            # aplicar filtros si existen
            if filters:
                queryset = super().apply_filters(queryset, filters)
                
            cache.set(cache_key, queryset, self.cache_timeout) 
        return queryset
    
    @transaction.atomic
    def create(self, entity: Order, order_items: List[OrderItem] = None) -> Order:
        entity.save()
        
        if order_items:
            for item in order_items:
                item.order = entity
                item.save()
        
        cache.delete_pattern('orders_*')
        cache_key = f'order_{entity.id}'
        cache.set(cache_key, entity, self.cache_timeout)
        return entity
    
    @transaction.atomic
    def update(self, entity: Order) -> Order:
        existing = Order.objects.filter(id=entity.id).first()
        if not existing:
            return None
        
        changed_fields = []
        for field in ['status', 'delivery_address', 'special_instructions', 
                     'estimated_delivery_time', 'is_active', 'total_amount']:
            if getattr(entity, field) != getattr(existing, field):
                changed_fields.append(field)
        
        if not changed_fields:
            return existing
        
        # actualizar solo los campos que cambiaron
        entity.save(update_fields=changed_fields + ['updated_at'])
        
        cache.delete(f'order_{entity.id}')
        cache.delete_pattern('orders_*')
        return entity
    
    @transaction.atomic
    def delete(self, id: int) -> bool:
        try:
            order = Order.objects.get(id=id)
            order.is_active = False
            order.save(update_fields=['is_active', 'updated_at'])
            
            cache.delete(f'order_{id}')
            cache.delete_pattern('orders_*')
            return True
        except Order.DoesNotExist:
            return False


class OrderItemRepository(DjangoRepository[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)
    
    def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        return OrderItem.objects.filter(order_id=order_id, is_active=True)
    
    @transaction.atomic
    def create_batch(self, items: List[OrderItem]) -> List[OrderItem]:
        return OrderItem.objects.bulk_create(items)
    
    @transaction.atomic
    def update_batch(self, items: List[OrderItem]) -> List[OrderItem]:
        updated_items = []
        
        for item in items:
            if item.id:
                item.save()
                updated_items.append(item)
        return updated_items
    
    @transaction.atomic
    def delete_by_order_id(self, order_id: int) -> int:
        """Marcar como inactivos todos los items de una orden"""
        count = OrderItem.objects.filter(order_id=order_id).update(
            is_active=False
        )
        return count
