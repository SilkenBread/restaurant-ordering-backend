from django.urls import path
from .views.order_views import OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('<int:order_id>/', OrderRetrieveUpdateDestroyAPIView.as_view(), name='order-detail')
]
