from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.utils.translation import gettext_lazy as _
from apps.core.exceptions import ValidationException
from apps.restaurants.dtos.restaurant_dto import RestaurantDTO
from apps.restaurants.repositories.restaurant_repository import RestaurantRepository
from apps.restaurants.serializers.restaurant_serializers import RestaurantDTOSerializer, RestaurantListDTOSerializer
from ..services.restaurant_services import RestaurantService


class RestaurantListCreateAPIView(APIView):
    """
    API para listar y crear restaurantes
    """
    service = RestaurantService(repository=RestaurantRepository())

    @extend_schema(
        operation_id="restaurants_list",
        summary="Obtener lista de restaurantes",
        description="Obtiene una lista paginada de restaurantes con filtros opcionales.",
        parameters=[
            OpenApiParameter(name='page', description='Número de página', required=False, type=int),
            OpenApiParameter(name='page_size', description='Tamaño de página', required=False, type=int),
            OpenApiParameter(name='name', description='Filtrar por nombre (contiene)', required=False, type=str),
            OpenApiParameter(name='address', description='Filtrar por dirección (contiene)', required=False, type=str),
            OpenApiParameter(name='rating_min', description='Rating mínimo (0.0-5.0)', required=False, type=float),
            OpenApiParameter(name='rating_max', description='Rating máximo (0.0-5.0)', required=False, type=float),
            OpenApiParameter(name='status', description='Estado (open/closed/maintenance)', required=False, type=str),
            OpenApiParameter(name='category', description='Categoría exacta', required=False, type=str),
            OpenApiParameter(name='is_active', description='Filtrar por activos (true/false)', required=False, type=bool),
            OpenApiParameter(
                name='location', 
                description='Filtrar por ubicación (lat,lon,distancia_km)', 
                required=False, 
                type=str,
                examples=[
                    OpenApiExample(
                        'Ejemplo ubicación',
                        value='40.4168,-3.7038,5',
                        description='Restaurantes dentro de 5km de Madrid centro'
                    )
                ]
            ),
        ],
        responses={
            200: RestaurantListDTOSerializer,
            400: None,
            401: None,
            500: None
        }
    )
    def get(self, request, restaurant_id=None):
        try:
            if restaurant_id:
                restaurant = self.service.get_restaurant(restaurant_id)
                serializer = RestaurantDTOSerializer(restaurant)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            pagination = {
                'page': int(request.query_params.get('page', 1)),
                'page_size': int(request.query_params.get('page_size', 10))
            }
            
            filters = request.query_params.dict()
            restaurants = self.service.list_restaurants(filters=filters, pagination=pagination)
            serializer = RestaurantListDTOSerializer(restaurants)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @extend_schema(
        operation_id="restaurants_create",
        summary="Crear un nuevo restaurante",
        description="Crea un nuevo restaurante con los datos proporcionados.",
        request=RestaurantDTOSerializer,
        responses={
            201: RestaurantDTOSerializer,
            400: None,
            401: None,
            403: None,
            500: None
        },
        examples=[
            OpenApiExample(
                'Ejemplo creación',
                value={
                    'name': 'Nuevo Restaurante',
                    'address': 'Calle Ejemplo 123',
                    'rating': 4.5,
                    'status': 'open',
                    'category': 'Italiano',
                    'latitude': 40.4168,
                    'longitude': -3.7038,
                    'is_active': True
                }
            )
        ]
    )
    def post(self, request):
        try:
            restaurant_data = RestaurantDTO(**request.data)
            created = self.service.create_restaurant(restaurant_data)
            return Response(created.__dict__, status=status.HTTP_201_CREATED)
        except ValidationException as e:
            return Response({'error': str(e), 'details': e.details}, 
                           status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RestaurantRetrieveUpdateDestroyAPIView(APIView):
    """
    APIs para obtener, actualizar y eliminar un restaurante
    """
    service = RestaurantService(repository=RestaurantRepository())

    @extend_schema(
        operation_id="restaurants_retrieve",
        summary="Obtener un restaurante por ID",
        description="Obtiene los detalles de un restaurante específico.",
        parameters=[
            OpenApiParameter(name='restaurant_id', description='ID del restaurante', required=True, type=int)
        ],
        responses={
            200: RestaurantDTOSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
            500: None
        }
    )
    def get(self, request, restaurant_id):
        try:
            restaurant = self.service.get_restaurant(restaurant_id)
            serializer = RestaurantDTOSerializer(restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        operation_id="restaurants_update",
        summary="Actualizar un restaurante",
        description="Actualiza un restaurante existente con los datos proporcionados.",
        request= RestaurantDTOSerializer,
        responses={
            200: RestaurantDTOSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
            500: None
        }
    )
    def put(self, request, restaurant_id):
        try:
            restaurant_data = RestaurantDTO(**request.data)
            updated = self.service.update_restaurant(restaurant_id, restaurant_data)
            return Response(updated.__dict__, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationException as e:
            return Response({'error': str(e), 'details': e.details}, 
                           status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @extend_schema(
        operation_id="restaurants_delete",
        summary="Eliminar un restaurante",
        description="Elimina un restaurante existente.",
        responses={
            204: None,
            401: None,
            403: None,
            404: None,
            500: None
        }
    )
    def delete(self, request, restaurant_id):
        try:
            deleted = self.service.delete_restaurant(restaurant_id)
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': _("Restaurante no encontrado")}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
