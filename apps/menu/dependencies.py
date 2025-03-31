from apps.menu.repositories.menuitem_repository import MenuItemRepository
from apps.menu.services.meuitem_service import MenuItemService

# Singleton instances
repository = MenuItemRepository()
service = MenuItemService(repository=repository)

def get_menu_item_repository():
    return repository

def get_menu_item_service():
    return service
