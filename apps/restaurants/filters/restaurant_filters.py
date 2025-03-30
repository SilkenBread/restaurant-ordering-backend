import django_filters
from django.db import models
from apps.core.filters.base_filters import BaseFilter
from ..models import Restaurant

class RestaurantFilter(BaseFilter):
    """
    Filtros avanzados para restaurantes.
    
    Filtros disponibles:
    - name: Búsqueda por nombre (contiene, case insensitive)
    - address: Búsqueda por dirección (contiene)
    - rating_min: Filtra por rating mínimo
    - rating_max: Filtra por rating máximo
    - status: Filtra por estado (open/closed/maintenance)
    - category: Filtra por categoría (exacto)
    - is_active: Filtra por estado activo/inactivo
    - location: Filtra por proximidad a coordenadas (lat,lon,distance)
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    location = django_filters.CharFilter(method='filter_by_location') # Filtro personalizado para ubicación

    class Meta(BaseFilter.Meta):
        model = Restaurant
        fields = BaseFilter.Meta.fields + [
            'name', 'address', 'rating_min', 'rating_max',
            'status', 'category', 'is_active'
        ]
    
    def filter_by_location(self, queryset, name, value):
        """
        Filtra restaurantes por proximidad a unas coordenadas.
        Formato esperado: lat,lon,distance (distance en km)
        """
        try:
            lat, lon, distance = map(float, value.split(','))
            # Usamos fórmula haversine para calcular distancia
            return queryset.annotate(
                distance=models.ExpressionWrapper(
                    models.Func(
                        models.Value(lat),
                        models.Value(lon),
                        models.F('latitude'),
                        models.F('longitude'),
                        function='ST_DistanceSphere',
                    ),
                    output_field=models.FloatField()
                )
            ).filter(distance__lte=distance * 1000)  # Convertir km a metros
        except (ValueError, AttributeError):
            return queryset
