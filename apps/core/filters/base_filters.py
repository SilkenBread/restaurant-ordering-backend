import django_filters

class BaseFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        fields = ['created_at', 'updated_at']
