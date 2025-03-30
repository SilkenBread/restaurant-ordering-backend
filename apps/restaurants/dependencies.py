from .repositories.restaurant_repository import RestaurantRepository
from .services.restaurant_services import RestaurantService

repository = RestaurantRepository()
service = RestaurantService(repository=repository)

def get_restaurant_service():
    return service
