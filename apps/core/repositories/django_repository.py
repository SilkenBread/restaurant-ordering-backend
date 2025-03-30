from django.db import transaction
from typing import Type, Dict, Any, Optional
from .base import BaseRepository, T

class DjangoRepository(BaseRepository[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model_class.objects.get(pk=id)
        except self.model_class.DoesNotExist:
            return None
        
    def get_all(self, filters: Optional[Dict[str, Any]] = None):
        queryset = self.model_class.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @transaction.atomic
    def create(self, entity: T) -> T:
        entity.save()
        return entity
    
    @transaction.atomic
    def update(self, entity: T) -> T:
        entity.save()
        return entity
    
    @transaction.atomic
    def delete(self, id: int) -> bool:
        rows_deleted, _ = self.model_class.objects.filter(pk=id).delete()
        return rows_deleted > 0
