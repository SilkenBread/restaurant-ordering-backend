from apps.core.filters.base_filters import BaseFilter
import django_filters
from django.db.models import Q
from ..models import MenuItem


class MenuItemFilter(BaseFilter):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(lookup_expr='iexact')
    restaurant = django_filters.NumberFilter(field_name='restaurant_id')
    max_preparation_time = django_filters.NumberFilter(field_name='preparation_time', lookup_expr='lte')
    is_available = django_filters.BooleanFilter()
    
    # Búsqueda combinada por nombre o descripción
    search = django_filters.CharFilter(method='filter_by_search')
    
    class Meta(BaseFilter.Meta):
        model = MenuItem
        fields = BaseFilter.Meta.fields + [
            'name', 'category', 'restaurant', 'is_active', 
            'is_available', 'min_price', 'max_price'
        ]
    
    def filter_by_search(self, queryset, name, value):
        """Filtrar por nombre o descripción"""
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        ).distinct()
