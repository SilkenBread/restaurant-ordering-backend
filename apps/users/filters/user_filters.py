import django_filters as filters
from ..models import User

class UserFilter(filters.FilterSet):
    email = filters.CharFilter(lookup_expr='icontains')
    is_active = filters.BooleanFilter()
    restaurant_id = filters.NumberFilter(field_name='restaurant__id')
    search = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['email', 'is_active', 'restaurant_id', 'search']
