from apps.core.filters.base_filters import BaseFilter
import django_filters
from django.db.models import Q
from apps.users.models import User


class UserFilter(BaseFilter):
    email = django_filters.CharFilter(lookup_expr='iexact')
    email_contains = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    restaurant = django_filters.NumberFilter(field_name='restaurant_id')
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()
    
    # Búsqueda combinada
    search = django_filters.CharFilter(method='filter_by_search')
    
    class Meta(BaseFilter.Meta):
        model = User
        fields = BaseFilter.Meta.fields + [
            'email', 'first_name', 'last_name', 'phone', 
            'restaurant', 'is_active', 'is_staff', 'is_superuser'
        ]
    
    def filter_by_search(self, queryset, name, value):
        """Filtrar por email, nombre o apellido"""
        return queryset.filter(
            Q(email__icontains=value) | 
            Q(first_name__icontains=value) | 
            Q(last_name__icontains=value)
        ).distinct()
