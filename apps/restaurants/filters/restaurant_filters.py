import django_filters as filters
from ..models import Restaurant

class RestaurantFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='icontains')
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    status = filters.CharFilter()

    class Meta:
        model = Restaurant
        fields = ['name', 'category', 'status', 'is_active']
