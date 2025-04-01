from apps.menu.repositories.menu_repository import MenuItemRepository
from apps.menu.services.menu_service import MenuService


repository = MenuItemRepository()
service = MenuService(repository=repository)

def get_menu_service():
    """Obtener una instancia del servicio de menu"""
    return service
