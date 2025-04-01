from django.urls import path
from .views import (
    MenuItemListCreateAPIView, 
    MenuItemRetrieveUpdateDestroyAPIView,
    RestaurantMenuItemsAPIView
)

urlpatterns = [
    path('', MenuItemListCreateAPIView.as_view(), name='menu-item-list-create'),
    path('<int:menu_item_id>/', MenuItemRetrieveUpdateDestroyAPIView.as_view(), name='menu-item-detail'),
    path('restaurant/<int:restaurant_id>/', RestaurantMenuItemsAPIView.as_view(), name='restaurant-menu-items'),
]
