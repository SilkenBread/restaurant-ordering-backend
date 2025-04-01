from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.core.decorators import permission_required
from apps.core.exceptions import ValidationException

from ..dependencies import get_menu_service
from ..serializers import MenuItemDTOSerializer
from ..dtos import MenuItemCreateDTO

# Obtener servicio
service = get_menu_service()


class MenuItemListCreateAPIView(APIView):
    pagination_class = PageNumberPagination
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
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
    
    @permission_required(['menu.view_menuitem'])
    def get(self, request):
        try:
            # Extraer filtros de los parámetros de consulta
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            # Obtener queryset filtrado
            queryset = service.list_menu_items(filters=filters)
            
            # Aplicar paginación
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Convertir a DTOs y serializar
                dto_items = [service._to_dto(item) for item in page]
                serializer = MenuItemDTOSerializer(dto_items, many=True)
                return self.get_paginated_response(serializer.data)
            
            # Si la paginación está desactivada
            dto_items = [service._to_dto(item) for item in queryset]
            serializer = MenuItemDTOSerializer(dto_items, many=True)
            return Response({
                'items': serializer.data,
                'total': len(dto_items),
                'page': 1,
                'page_size': len(dto_items)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @permission_required(['menu.add_menuitem'])
    def post(self, request):
        try:
            # Convertir datos de entrada a DTO
            # Necesitamos manejar la imagen de forma especial si está presente
            data = request.data.copy()
            
            # Crear DTO
            menu_item_data = MenuItemCreateDTO(
                name=data.get('name'),
                description=data.get('description'),
                price=float(data.get('price')),
                preparation_time=int(data.get('preparation_time')),
                category=data.get('category'),
                restaurant_id=int(data.get('restaurant_id')),
                is_active=data.get('is_active', True) in [True, 'true', 'True', '1', 1],
                is_available=data.get('is_available', True) in [True, 'true', 'True', '1', 1],
                image=request.FILES.get('image') if 'image' in request.FILES else None
            )
            
            # Crear ítem de menú
            response_data = service.create_menu_item(menu_item_data)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValidationException as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MenuItemRetrieveUpdateDestroyAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    @permission_required(['menu.view_menuitem'])
    def get(self, request, menu_item_id):
        try:
            # Obtener ítem de menú por ID
            menu_item = service.get_menu_item(menu_item_id)
            serializer = MenuItemDTOSerializer(menu_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @permission_required(['menu.change_menuitem'])
    def put(self, request, menu_item_id):
        try:
            # Gestionar los datos del formulario multipart
            data = request.data.copy()
            
            # Si hay imagen, añadirla
            if 'image' in request.FILES:
                data['image'] = request.FILES.get('image')
            
            # Actualizar ítem de menú
            response_data = service.update_menu_item(menu_item_id, data)
            return Response(response_data, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationException as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @permission_required(['menu.delete_menuitem'])
    def delete(self, request, menu_item_id):
        try:
            # Eliminar ítem de menú (marcar como inactivo)
            deleted = service.delete_menu_item(menu_item_id)
            
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response({
                'status': 'error',
                'message': 'Ítem de menú no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantMenuItemsAPIView(APIView):
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
    
    @permission_required(['menu.view_menuitem'])
    def get(self, request, restaurant_id):
        try:
            # Obtener menú de un restaurante específico
            menu_items = service.get_restaurant_menu(restaurant_id)
            
            # Serializar los DTOs
            serializer = MenuItemDTOSerializer(menu_items, many=True)
            
            return Response({
                'items': serializer.data,
                'total': len(menu_items),
                'restaurant_id': restaurant_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
