from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action


from .repositories.restaurant_repository import RestaurantRepository
from .services.restaurant_services import RestaurantService
from .dtos.restaurant_filter_dto import RestaurantFilterDTO
from .dtos.restaurant_dto import RestaurantDTO
from .serializers import RestaurantSerializer


class RestaurantViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones CRUD de restaurantes
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RestaurantService(RestaurantRepository())
    
    def list(self, request):
        # Validación básica con DTO
        filter_dto = RestaurantFilterDTO(
            name=request.query_params.get('name'),
            status=request.query_params.get('status'),
            category=request.query_params.get('category'),
            min_rating=request.query_params.get('min_rating'),
            max_rating=request.query_params.get('max_rating'),
        )
        
        validation_errors = filter_dto.validate()
        if validation_errors:
            return Response({'errors': validation_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrado avanzado con django-filters
        filtered_queryset = self.service.get_filtered_queryset(request.query_params)
        serializer = RestaurantSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        try:
            restaurant_dto = RestaurantDTO(**request.data)
            restaurant = self.service.create_restaurant(restaurant_dto)
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        restaurant = self.service.get_restaurant(pk)
        if not restaurant:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        try:
            restaurant_dto = RestaurantDTO(**request.data)
            restaurant = self.service.update_restaurant(pk, restaurant_dto)
            if not restaurant:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        try:
            # Para PATCH, solo actualizamos los campos proporcionados
            existing = self.service.get_restaurant(pk)
            if not existing:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            restaurant_dto = RestaurantDTO(
                name=request.data.get('name', existing.name),
                address=request.data.get('address', existing.address),
                rating=request.data.get('rating', existing.rating),
                status=request.data.get('status', existing.status),
                category=request.data.get('category', existing.category),
                latitude=request.data.get('latitude', existing.latitude),
                longitude=request.data.get('longitude', existing.longitude),
                is_active=request.data.get('is_active', existing.is_active)
            )
            
            restaurant = self.service.update_restaurant(pk, restaurant_dto)
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        success = self.service.delete_restaurant(pk)
        if not success:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Endpoint personalizado para activar un restaurante"""
        restaurant = self.service.get_restaurant(pk)
        if not restaurant:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        restaurant.is_active = True
        restaurant.save()
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Endpoint personalizado para desactivar un restaurante"""
        restaurant = self.service.get_restaurant(pk)
        if not restaurant:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        restaurant.is_active = False
        restaurant.save()
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
