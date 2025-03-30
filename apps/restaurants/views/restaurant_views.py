from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.utils.translation import gettext_lazy as _
from apps.core.exceptions import ValidationException
from apps.restaurants.dtos.restaurant_dto import RestaurantCreateDTO, RestaurantDTO, RestaurantUpdateDTO
from apps.restaurants.repositories.restaurant_repository import RestaurantRepository
from apps.restaurants.serializers.restaurant_serializers import RestaurantDTOSerializer, RestaurantListDTOSerializer
from ..services.restaurant_services import RestaurantService
from rest_framework.pagination import PageNumberPagination

class RestaurantListCreateAPIView(APIView):
    service = RestaurantService(repository=RestaurantRepository())
    pagination_class = PageNumberPagination

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = PageNumberPagination()
            # Permitir personalizar el tamaño de página
            page_size = self.request.query_params.get('page_size')
            if page_size:
                try:
                    self._paginator.page_size = int(page_size)
                except ValueError:
                    pass  # usa tamaño por defecto
        return self._paginator
    
    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return Response({
            'items': data,
            'total': self.paginator.page.paginator.count,
            'page': self.paginator.page.number,
            'page_size': self.paginator.page_size,
        })
    
    def get(self, request, restaurant_id=None):
        try:
            # Si se solicita un restaurante específico
            if restaurant_id:
                restaurant = self.service.get_restaurant(restaurant_id)
                serializer = RestaurantDTOSerializer(restaurant)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Extraer filtros de los parámetros de consulta
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            # Obtener queryset filtrado
            queryset = self.service.list_restaurants(filters=filters)
            
            # Aplicar paginación
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Convertir a DTOs y serializar
                dto_items = [self.service._to_dto(item) for item in page]
                serializer = RestaurantDTOSerializer(dto_items, many=True)
                return self.get_paginated_response(serializer.data)
            
            # Si la paginación está desactivada (poco probable con tu configuración)
            dto_items = [self.service._to_dto(item) for item in queryset]
            serializer = RestaurantDTOSerializer(dto_items, many=True)
            return Response({
                'items': serializer.data,
                'total': len(dto_items),
                'page': 1,
                'page_size': len(dto_items)
            }, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            restaurant_data = RestaurantCreateDTO(**request.data)
            created = self.service.create_restaurant(restaurant_data)
            return Response(self.service._to_dto(created).__dict__, status=status.HTTP_201_CREATED)
        except ValidationException as e:
            return Response({
                "status": "error",
                "code": e.default_code,
                "message": e.detail,
                "errors": e.errors
            }, status=e.status_code)
        except Exception as e:
            return Response({
                "status": "error",
                "code": "server_error",
                "message": "Error interno del servidor",
                "errors": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RestaurantRetrieveUpdateDestroyAPIView(APIView):
    service = RestaurantService(repository=RestaurantRepository())

    def get(self, request, restaurant_id):
        try:
            restaurant = self.service.get_restaurant(restaurant_id)
            serializer = RestaurantDTOSerializer(restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, restaurant_id):
        try:
            restaurant_data = RestaurantUpdateDTO(**request.data)
            updated = self.service.update_restaurant(restaurant_id, restaurant_data)
            return Response(self.service._to_dto(updated).__dict__, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({
                "status": "error",
                "code": "not_found",
                "message": str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationException as e:
            return Response({
                "status": "error",
                "code": "validation_error",
                "message": str(e.detail),
                "errors": e.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "code": "server_error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, restaurant_id):
        try:
            deleted = self.service.delete_restaurant(restaurant_id)
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': _("Restaurante no encontrado")}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
