from django.core.exceptions import ObjectDoesNotExist
from typing import List, Optional, Dict
from ..models import Restaurant
from .interfaces import IRestaurantRepository

class RestaurantRepository(IRestaurantRepository):
    def get_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        try:
            return Restaurant.objects.get(pk=restaurant_id, is_active=True)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self) -> List[Restaurant]:
        return Restaurant.objects.filter(is_active=True).all()
    
    def create(self, restaurant_data: dict) -> Restaurant:
        return Restaurant.objects.create(**restaurant_data)
    
    def update(self, restaurant: Restaurant, restaurant_data: dict) -> Restaurant:
        for attr, value in restaurant_data.items():
            setattr(restaurant, attr, value)
        restaurant.save()
        return restaurant
    
    def delete(self, restaurant: Restaurant) -> None:
        restaurant.is_active = False
        restaurant.save()

    def filter(self, filters: Dict = None, queryset=None) -> List[Restaurant]:
        if queryset is None:
            queryset = Restaurant.objects.filter(is_active=True)
        
        if filters:
            queryset = queryset.filter(**filters)
        
        return queryset.all()
