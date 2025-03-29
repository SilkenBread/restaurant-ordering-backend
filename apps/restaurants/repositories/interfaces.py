from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Restaurant

class IRestaurantRepository(ABC):
    @abstractmethod
    def get_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Restaurant]:
        pass
    
    @abstractmethod
    def create(self, restaurant_data: dict) -> Restaurant:
        pass
    
    @abstractmethod
    def update(self, restaurant: Restaurant, restaurant_data: dict) -> Restaurant:
        pass
    
    @abstractmethod
    def delete(self, restaurant: Restaurant) -> None:
        pass
    
    @abstractmethod
    def filter(self, filters: dict) -> List[Restaurant]:
        pass
