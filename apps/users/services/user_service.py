from typing import Dict, Any, Optional, List, Union
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound

from apps.users.models import User
from apps.users.filters import UserFilter
from apps.users.repositories import UserRepository
from apps.users.dtos import UserDTO, UserCreateDTO, UserUpdateDTO
from apps.users.serializers import (
    UserDTOSerializer,
    UserCreateDTOSerializer,
    UserUpdateDTOSerializer
)
from apps.core.exceptions import ValidationException


class UserService:
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()
    
    def _format_validation_error(self, serializer_errors):
        """Formatea errores de validación para una respuesta consistente"""
        return {
            "status": "error",
            "code": "validation_error",
            "message": _("Error de validación en los datos proporcionados"),
            "errors": serializer_errors
        }
    
    def get_user(self, user_id: int) -> Optional[UserDTO]:
        """Obtiene un usuario por su ID"""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFound(_("Usuario no encontrado"))
        
        # Convertir a DTO
        return self._to_dto(user)
    
    def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """Obtiene un usuario por su email"""
        user = self.repository.get_by_email(email)
        if not user:
            raise NotFound(_("Usuario no encontrado"))
        
        # Convertir a DTO
        return self._to_dto(user)
    
    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        """Lista usuarios con filtros opcionales"""
        base_queryset = self.repository.get_all()
        
        # Aplicar filtros
        filter_set = UserFilter(filters or {}, queryset=base_queryset)
        filtered_queryset = filter_set.qs
        
        return filtered_queryset.order_by('last_name', 'first_name')
    
    def get_restaurant_users(self, restaurant_id: int) -> List[UserDTO]:
        """Obtiene todos los usuarios de un restaurante específico"""
        users = self.repository.get_by_restaurant_id(restaurant_id)
        return [self._to_dto(user) for user in users]
    
    @transaction.atomic
    def create_user(self, user_data: UserCreateDTO) -> Dict:
        """Crea un nuevo usuario"""
        try:
            # Validar datos de entrada
            serializer = UserCreateDTOSerializer(data=user_data.__dict__)
            serializer.is_valid(raise_exception=True)
            
            # Verificar si el email ya existe
            if self.repository.get_by_email(user_data.email):
                raise ValidationException(detail={
                    "status": "error",
                    "code": "email_exists",
                    "message": _("Ya existe un usuario con este correo electrónico")
                })
            
            # Crear usuario
            user = self._to_model(user_data)
            created_user = self.repository.create(user)
            
            # Retornar DTO serializado
            return UserDTOSerializer(self._to_dto(created_user)).data
            
        except ValidationError as e:
            # Centralizar manejo de errores de validación
            raise ValidationException(detail=self._format_validation_error(e.detail))
        except ValidationException as e:
            raise e
        except Exception as e:
            # Centralizar manejo de errores generales
            raise ValidationException(detail={
                "status": "error",
                "code": "create_error",
                "message": str(e)
            })
    
    @transaction.atomic
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        """Actualiza un usuario existente"""
        try:
            # Verificar que el usuario exista
            existing = self.repository.get_by_id(user_id)
            if not existing:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Usuario no encontrado")
                })
            
            # Validar datos de actualización
            serializer = UserUpdateDTOSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar si hay campos para actualizar
            if not serializer.validated_data:
                return {
                    "status": "success",
                    "code": "no_changes",
                    "message": _("No se proporcionaron campos para actualizar"),
                    "data": UserDTOSerializer(self._to_dto(existing)).data
                }
            
            # Verificar si se intenta cambiar el email a uno que ya existe
            if 'email' in serializer.validated_data and serializer.validated_data['email'] != existing.email:
                if self.repository.get_by_email(serializer.validated_data['email']):
                    raise ValidationException(detail={
                        "status": "error",
                        "code": "email_exists",
                        "message": _("Ya existe un usuario con este correo electrónico")
                    })
            
            # Crear un objeto con los datos a actualizar
            update_dto = UserUpdateDTO(**serializer.validated_data)
            update_model = self._to_model(update_dto, existing)
            
            # Guardar cambios
            updated_user = self.repository.update(update_model)
            
            return UserDTOSerializer(self._to_dto(updated_user)).data
            
        except ValidationError as e:
            raise ValidationException(detail=self._format_validation_error(e.detail))
        except NotFound as e:
            raise e
        except ValidationException as e:
            raise e
        except Exception as e:
            raise ValidationException(detail={
                "status": "error",
                "code": "update_error",
                "message": str(e)
            })
    
    def delete_user(self, user_id: int) -> bool:
        """Elimina (marca como inactivo) un usuario"""
        return self.repository.delete(user_id)
    
    def _to_dto(self, model: User) -> UserDTO:
        """Convierte un modelo User a su DTO"""
        return UserDTO(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            default_address=model.default_address,
            restaurant_id=model.restaurant_id,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            is_active=model.is_active,
            date_joined=model.date_joined,
            last_updated=model.last_updated
        )
    
    def _to_model(self, dto: Union[UserCreateDTO, UserUpdateDTO, UserDTO], existing_model: User = None) -> User:
        """Convierte un DTO a modelo User"""
        model = existing_model or User()
        
        if isinstance(dto, UserDTO) and dto.id:
            model.id = dto.id
        
        for field in ['email', 'first_name', 'last_name', 'phone', 
                     'default_address', 'restaurant_id', 'is_staff', 
                     'is_superuser', 'is_active']:
            if hasattr(dto, field) and getattr(dto, field) is not None:
                setattr(model, field, getattr(dto, field))
        
        # Manejar la contraseña de forma especial
        if hasattr(dto, 'password') and dto.password:
            model._password = dto.password
        
        return model
