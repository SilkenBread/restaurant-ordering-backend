from django.urls import path
from .views.restaurant_views import RestaurantListCreateAPIView, RestaurantRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', RestaurantListCreateAPIView.as_view(), name='restaurants-list'),
    path('<int:restaurant_id>/', RestaurantRetrieveUpdateDestroyAPIView.as_view(), name='restaurants-detail'),
]
