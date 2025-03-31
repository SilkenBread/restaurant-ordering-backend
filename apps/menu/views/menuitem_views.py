from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from apps.menu.dependencies import get_menu_item_service
from apps.menu.serializers.menuitem_serializer import MenuItemDTOSerializer

service = get_menu_item_service()

class MenuItemListCreateAPIView(APIView):
    pagination_class = PageNumberPagination
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
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
    
    @method_decorator(permission_required(['menu.view_menuitem']))
    def get(self, request):
        try:
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            queryset = service.list_menu_items(filters=filters)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                dto_items = [service._to_dto(item) for item in page]
                serializer = MenuItemDTOSerializer(dto_items, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            dto_items = [service._to_dto(item) for item in queryset]
            serializer = MenuItemDTOSerializer(dto_items, many=True, context={'request': request})
            return Response({
                'items': serializer.data,
                'total': len(dto_items),
                'page': 1,
                'page_size': len(dto_items)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(getattr(e, 'detail', {'error': str(e)}), 
                            status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))
    
    @method_decorator(permission_required(['menu.add_menuitem']))
    def post(self, request):
        try:
            # Extraer archivo de imagen si está presente
            image_file = request.FILES.get('image')
            if image_file:
                # Añadir la request al archivo para poder construir URLs absolutas
                image_file._request = request
            
            # Extraer datos del formulario o JSON
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data
            
            response_data = service.create_menu_item(data, image_file)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(getattr(e, 'detail', {'error': str(e)}), 
                            status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))

class MenuItemRetrieveUpdateDestroyAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    @method_decorator(permission_required(['menu.view_menuitem']))
    def get(self, request, menu_item_id):
        try:
            menu_item = service.get_menu_item(menu_item_id)
            serializer = MenuItemDTOSerializer(menu_item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(getattr(e, 'detail', {'error': str(e)}), 
                            status=getattr(e, 'status_code', status.HTTP_404_NOT_FOUND))
        
    @method_decorator(permission_required(['menu.change_menuitem']))
    def put(self, request, menu_item_id):
        try:
            # Extraer archivo de imagen si está presente
            image_file = request.FILES.get('image')
            if image_file:
                # Añadir la request al archivo para poder construir URLs absolutas
                image_file._request = request
            
            # Extraer datos del formulario o JSON
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data
            
            # Manejar caso especial para eliminar la imagen
            if 'remove_image' in data and data['remove_image'].lower() in ['true', '1', 'yes']:
                data['image'] = None
            
            response_data = service.update_menu_item(menu_item_id, data, image_file)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(getattr(e, 'detail', {'error': str(e)}), 
                            status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))
    
    @method_decorator(permission_required(['menu.delete_menuitem']))
    def delete(self, request, menu_item_id):
        try:
            service.delete_menu_item(menu_item_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(getattr(e, 'detail', {'error': str(e)}), 
                            status=getattr(e, 'status_code', status.HTTP_404_NOT_FOUND))
