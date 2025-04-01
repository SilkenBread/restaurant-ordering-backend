from apps.core.filters.base_filters import BaseFilter
import django_filters
from ..models import Order


class OrderFilter(BaseFilter):
    customer = django_filters.NumberFilter(field_name='customer_id')
    restaurant = django_filters.NumberFilter(field_name='restaurant_id')
    status = django_filters.CharFilter(field_name='status')
    min_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    date_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # buscar por direccion de entrega
    delivery_address = django_filters.CharFilter(lookup_expr='icontains')
    
    # buscar ordenes con elementos especificos
    menu_item = django_filters.NumberFilter(method='filter_by_menu_item')
    
    class Meta(BaseFilter.Meta):
        model = Order
        fields = BaseFilter.Meta.fields + [
            'customer', 'restaurant', 'status', 'min_amount', 
            'max_amount', 'delivery_address', 'is_active'
        ]
    
    def filter_by_menu_item(self, queryset, name, value):
        """Filtrar órdenes que contengan un item de menú específico"""
        return queryset.filter(order_items__menu_item_id=value).distinct()
