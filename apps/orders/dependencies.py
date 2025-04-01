from .repositories.order_repository import OrderRepository, OrderItemRepository
from .services.order_service import OrderService

order_repository = OrderRepository()
order_item_repository = OrderItemRepository()

service = OrderService(
    order_repository=order_repository,
    order_item_repository=order_item_repository
)

def get_order_service():
    return service
