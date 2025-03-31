from django.urls import path
from .views.menuitem_views import MenuItemListCreateAPIView, MenuItemRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('items/', MenuItemListCreateAPIView.as_view(), name='menu-items-list-create'),
    path('items/<int:menu_item_id>/', MenuItemRetrieveUpdateDestroyAPIView.as_view(), name='menu-items-retrieve-update-destroy'),
]
