from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from ..dependencies import get_user_service
from ..serializers.user_serializers import UserDTOSerializer


service = get_user_service()

class UserListCreateAPIView(APIView):
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
    
    @method_decorator(permission_required(['users.view_user']))
    def get(self, request, user_id=None):
        try:
            if user_id:
                user = service.get_user(user_id)
                serializer = UserDTOSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            queryset = service.list_users(filters=filters)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                dto_items = [service._to_dto(item) for item in page]
                serializer = UserDTOSerializer(dto_items, many=True)
                return self.get_paginated_response(serializer.data)
            
            dto_items = [service._to_dto(item) for item in queryset]
            serializer = UserDTOSerializer(dto_items, many=True)
            return Response({
                'items': serializer.data,
                'total': len(dto_items),
                'page': 1,
                'page_size': len(dto_items)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required(['users.add_user']))
    def post(self, request):
        try:
            response_data = service.create_user(request.data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e.detail, status=e.status_code)

class UserRetrieveUpdateDestroyAPIView(APIView):
    @method_decorator(permission_required(['users.view_user']))
    def get(self, request, user_id):
        try:
            user = service.get_user(user_id)
            serializer = UserDTOSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e.detail, status=e.status_code)
        
    @method_decorator(permission_required(['users.change_user']))
    def put(self, request, user_id):
        try:
            response_data = service.update_user(user_id, request.data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e.detail, status=e.status_code)
    
    @method_decorator(permission_required(['users.delete_user']))
    def delete(self, request, user_id):
        try:
            service.delete_user(user_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(e.detail, status=e.status_code)
