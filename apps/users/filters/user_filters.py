from apps.core.filters.base_filters import BaseFilter
from apps.users.models import User
import django_filters

class UserFilter(BaseFilter):
    email = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()
    restaurant_id = django_filters.NumberFilter()

    class Meta(BaseFilter.Meta):
        model = User
        fields = BaseFilter.Meta.fields + [
            'email', 'first_name', 'last_name', 'phone',
            'is_active', 'is_staff', 'is_superuser', 'restaurant_id'
        ]
