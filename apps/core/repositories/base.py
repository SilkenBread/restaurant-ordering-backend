from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
