import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import NotFound
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from apps.core.decorators import permission_required
from apps.core.exceptions import ValidationException
from apps.users.dtos import UserCreateDTO
from apps.users.serializers.user_serializers import BulkUserUploadSerializer, UserDTOSerializer
from apps.users.services import UserService
from apps.users.tasks import process_bulk_users

# Inicializar el servicio
service = UserService()


class UserListCreateAPIView(APIView):
    pagination_class = PageNumberPagination
    parser_classes = (JSONParser,)
    
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
    
    @permission_required(['users.view_user'])
    def get(self, request):
        try:
            # Extraer filtros de los parámetros de consulta
            filters = request.query_params.dict()
            if 'page' in filters:
                filters.pop('page')
            if 'page_size' in filters:
                filters.pop('page_size')
            
            # Obtener queryset filtrado
            queryset = service.list_users(filters=filters)
            
            # Aplicar paginación
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Convertir a DTOs y serializar
                dto_items = [service._to_dto(item) for item in page]
                serializer = UserDTOSerializer(dto_items, many=True)
                return self.get_paginated_response(serializer.data)
            
            # Si la paginación está desactivada
            dto_items = [service._to_dto(item) for item in queryset]
            serializer = UserDTOSerializer(dto_items, many=True)
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
    
    def post(self, request):
        try:
            # Convertir datos de entrada a DTO
            data = request.data.copy()
            
            # Determinar si debe tener privilegios especiales
            # Solo usuarios autenticados con permisos adecuados pueden crear usuarios staff/superuser
            requires_admin_permission = False
            if data.get('is_staff') or data.get('is_superuser'):
                requires_admin_permission = True
            
            # Verificar permisos si se requieren
            if requires_admin_permission:
                if not request.user.is_authenticated or not request.user.has_perm('users.add_user'):
                    return Response({
                        'status': 'error',
                        'message': _("No tiene permisos para crear usuarios con privilegios administrativos")
                    }, status=status.HTTP_403_FORBIDDEN)
            
            # Crear DTO
            user_data = UserCreateDTO(
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                password=data.get('password'),
                phone=data.get('phone'),
                default_address=data.get('default_address'),
                restaurant_id=data.get('restaurant_id'),
                is_staff=data.get('is_staff', False) in [True, 'true', 'True', '1', 1],
                is_superuser=data.get('is_superuser', False) in [True, 'true', 'True', '1', 1],
                is_active=data.get('is_active', True) in [True, 'true', 'True', '1', 1]
            )
            
            # Crear usuario
            response_data = service.create_user(user_data)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValidationException as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRetrieveUpdateDestroyAPIView(APIView):
    parser_classes = (JSONParser,)
    
    @permission_required(['users.view_user'])
    def get(self, request, user_id):
        try:
            # Obtener usuario por ID
            user = service.get_user(user_id)
            serializer = UserDTOSerializer(user)
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
    
    @permission_required(['users.change_user'])
    def put(self, request, user_id):
        try:
            # Gestionar los datos
            data = request.data.copy()
            
            # Solo superusuarios pueden modificar estado de superusuario
            if 'is_superuser' in data and not request.user.is_superuser:
                return Response({
                    'status': 'error',
                    'message': _("Solo superusuarios pueden modificar el estado de superusuario")
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Actualizar usuario
            response_data = service.update_user(user_id, data)
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
    
    @permission_required(['users.delete_user'])
    def delete(self, request, user_id):
        try:
            # No permitir que un usuario se elimine a sí mismo
            if request.user.id == int(user_id):
                return Response({
                    'status': 'error',
                    'message': _("No puede desactivar su propio usuario")
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Eliminar usuario (marcar como inactivo)
            deleted = service.delete_user(user_id)
            
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response({
                'status': 'error',
                'message': _('Usuario no encontrado')
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkUserCreateAPIView(APIView):
    """
    Endpoint para creación masiva de usuarios mediante CSV
    """
    @permission_required(['users.add_user'])
    def post(self, request):
        serializer = BulkUserUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Leer el archivo
            csv_file = serializer.validated_data['file']
            file_content = csv_file.read().decode('utf-8')
            
            # Generar ID unico para la tarea
            task_id = str(uuid.uuid4())
            
            # Enviar tarea a Celery
            process_bulk_users.delay(file_content, task_id)
            
            return Response({
                'status': 'processing',
                'message': _("El archivo está siendo procesado"),
                'task_id': task_id,
                'monitor_url': f'/users/bulk/status/{task_id}'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class BulkUserTaskStatusAPIView(APIView):
    """
    Endpoint para consultar estado de tareas de carga masiva
    """
    @permission_required(['users.view_user'])
    def get(self, request, task_id):
        results = cache.get(f'bulk_user_task_{task_id}')
        
        if not results:
            return Response({
                'status': 'not_found',
                'message': _("Tarea no encontrada o expirada")
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response(results, status=status.HTTP_200_OK)
