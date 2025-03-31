from apps.core.filters.base_filters import BaseFilter
from apps.menu.models import MenuItem
import django_filters
from django.db.models import Q

class MenuItemFilter(BaseFilter):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    preparation_time_min = django_filters.NumberFilter(field_name='preparation_time', lookup_expr='gte')
    preparation_time_max = django_filters.NumberFilter(field_name='preparation_time', lookup_expr='lte')
    category = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_available = django_filters.BooleanFilter()
    restaurant_id = django_filters.NumberFilter()
    search = django_filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) | 
            Q(category__icontains=value)
        )
    
    class Meta(BaseFilter.Meta):
        model = MenuItem
        fields = BaseFilter.Meta.fields + [
            'name', 'description', 'price_min', 'price_max', 
            'preparation_time_min', 'preparation_time_max', 'category',
            'is_active', 'is_available', 'restaurant_id', 'search'
        ]
