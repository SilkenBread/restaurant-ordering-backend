from typing import List, Optional

from ..dtos.restaurant_dto import RestaurantDTO
from ..repositories.restaurant_repository import RestaurantRepository
from ..filters.restaurant_filters import RestaurantFilter
from ..models import Restaurant


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository
    
    def get_restaurant(self, restaurant_id: int) -> Optional[Restaurant]:
        return self.repository.get_by_id(restaurant_id)
    
    def get_all_restaurants(self) -> List[Restaurant]:
        return self.repository.get_all()
    
    def create_restaurant(self, restaurant_dto: RestaurantDTO) -> Restaurant:
        validation_errors = restaurant_dto.validate()
        if validation_errors:
            raise ValueError(validation_errors)
        
        restaurant_data = {
            'name': restaurant_dto.name,
            'address': restaurant_dto.address,
            'rating': restaurant_dto.rating,
            'status': restaurant_dto.status,
            'category': restaurant_dto.category,
            'latitude': restaurant_dto.latitude,
            'longitude': restaurant_dto.longitude,
            'is_active': restaurant_dto.is_active
        }
        return self.repository.create(restaurant_data)
    
    def update_restaurant(self, restaurant_id: int, restaurant_dto: RestaurantDTO) -> Optional[Restaurant]:
        restaurant = self.repository.get_by_id(restaurant_id)
        if not restaurant:
            return None
        
        validation_errors = restaurant_dto.validate()
        if validation_errors:
            raise ValueError(validation_errors)
        
        update_data = {
            'name': restaurant_dto.name,
            'address': restaurant_dto.address,
            'rating': restaurant_dto.rating,
            'status': restaurant_dto.status,
            'category': restaurant_dto.category,
            'latitude': restaurant_dto.latitude,
            'longitude': restaurant_dto.longitude,
            'is_active': restaurant_dto.is_active
        }
        return self.repository.update(restaurant, update_data)
    
    def delete_restaurant(self, restaurant_id: int) -> bool:
        restaurant = self.repository.get_by_id(restaurant_id)
        if not restaurant:
            return False
        
        self.repository.delete(restaurant)
        return True
    
    def filter_restaurants(self, filters=None, queryset=None) -> List[Restaurant]:
        return self.repository.filter(filters, queryset)
    
    def get_filtered_queryset(self, request_params):
        qs = Restaurant.objects.filter(is_active=True)
        restaurant_filter = RestaurantFilter(request_params, queryset=qs)
        return restaurant_filter.qs
