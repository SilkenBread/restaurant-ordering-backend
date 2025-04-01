from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

from apps.core.decorators import permission_required
from apps.core.exceptions import ValidationException
from apps.orders.dependencies import get_order_service

from ..serializers import OrderDTOSerializer
from ..dtos import OrderCreateDTO

# Obtener servicio
service = get_order_service()


class OrderListCreateAPIView(APIView):
    pagination_class = PageNumberPagination
    
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = PageNumberPagination()
            page_size = self.request.query_params.get('page_size')
            if page_size:
                try:
                    self._paginator.page_size = int(page_size)
                except ValueError:
                    pass
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
    
    @permission_required(['orders.view_order'])
    def get(self, request):
        try:
            # extraer filtros de los parámetros de consulta
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            # obtener queryset filtrado
            queryset = service.list_orders(filters=filters)
            
            # paginacion
            page = self.paginate_queryset(queryset)
            if page is not None:
                # convertir a DTOs y serializar
                dto_items = [service._to_dto(item) for item in page]
                serializer = OrderDTOSerializer(dto_items, many=True)
                return self.get_paginated_response(serializer.data)
            
            dto_items = [service._to_dto(item) for item in queryset]
            serializer = OrderDTOSerializer(dto_items, many=True)
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
    
    @permission_required(['orders.add_order'])
    def post(self, request):
        try:
            # convertir datos de entrada a DTO
            order_data = OrderCreateDTO(**request.data)
            
            # crear orden
            response_data = service.create_order(order_data)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValidationException as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderRetrieveUpdateDestroyAPIView(APIView):
    @permission_required(['orders.view_order'])
    def get(self, request, order_id):
        try:
            # obtener orden por ID
            order = service.get_order(order_id)
            serializer = OrderDTOSerializer(order)
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
    
    @permission_required(['orders.change_order'])
    def put(self, request, order_id):
        try:
            # actualizar orden
            response_data = service.update_order(order_id, request.data)
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
    
    @permission_required(['orders.delete_order'])
    def delete(self, request, order_id):
        try:
            # Eliminar orden (marcar como inactiva)
            deleted = service.delete_order(order_id)
            
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response({
                'status': 'error',
                'message': 'Orden no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
