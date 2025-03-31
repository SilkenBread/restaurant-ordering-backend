from typing import Dict, Optional, Any, Union
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, ValidationError

from ..dtos.user_dtos import UserCreateDTO, UserDTO, UserUpdateDTO
from ..filters.user_filters import UserFilter
from ..repositories.user_repository import UserRepository
from ..serializers.user_serializers import UserCreateDTOSerializer, UserDTOSerializer, UserUpdateDTOSerializer
from ..models import User
from rest_framework import serializers

class UserService:
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()

    def _format_validation_error(self, serializer_errors):
        return {
            "status": "error",
            "code": "validation_error",
            "message": _("Error de validación en los datos proporcionados"),
            "errors": serializer_errors
        }
    
    def get_user(self, user_id: int) -> Optional[UserDTO]:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFound(detail={
                "status": "error",
                "code": "not_found",
                "message": _("Usuario no encontrado")
            })
        return self._to_dto(user)
    
    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        try:
            base_queryset = self.repository.get_all()
            filter_set = UserFilter(filters or {}, queryset=base_queryset)
            return filter_set.qs.order_by('-date_joined')
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "filter_error",
                "message": str(e)
            })
        
    def create_user(self, user_data: Dict) -> Dict:
        try:
            serializer = UserCreateDTOSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            
            user = self._to_model(UserCreateDTO(**serializer.validated_data))
            created = self.repository.create(user)
            
            return UserDTOSerializer(self._to_dto(created)).data
            
        except serializers.ValidationError as e:
            raise ValidationError(detail=self._format_validation_error(e.detail))
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "create_error",
                "message": str(e)
            })
        
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        try:
            existing = self.repository.get_by_id(user_id)
            if not existing:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Usuario no encontrado")
                })
            
            serializer = UserUpdateDTOSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar campos para actualizar
            if not serializer.validated_data:
                return {
                    "status": "success",
                    "code": "no_changes",
                    "message": _("No se proporcionaron campos para actualizar"),
                    "data": UserDTOSerializer(self._to_dto(existing)).data
                }
            
            # Actualizar campos
            for field, value in serializer.validated_data.items():
                if field == 'password' and value:
                    existing.set_password(value)
                elif value is not None:  # Solo actualizar si el valor no es None
                    setattr(existing, field, value)
            
            updated = self.repository.update(existing)
            return UserDTOSerializer(self._to_dto(updated)).data
            
        except serializers.ValidationError as e:
            raise ValidationError(detail=self._format_validation_error(e.detail))
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "update_error",
                "message": str(e)
            })
    
    def delete_user(self, user_id: int) -> bool:
        try:
            deleted = self.repository.delete(user_id)
            if not deleted:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Usuario no encontrado")
                })
            return deleted
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "delete_error",
                "message": str(e)
            })
    
    def _to_dto(self, model: User) -> UserDTO:
        return UserDTO(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            default_address=model.default_address,
            restaurant_id=model.restaurant_id,
            is_active=model.is_active,
            date_joined=model.date_joined,
            last_updated=model.last_updated
        )
    
    def _to_model(self, dto: Union[UserCreateDTO, UserUpdateDTO, UserDTO]) -> User:
        model = self.repository.model_class()
        
        if isinstance(dto, UserDTO):
            model.id = dto.id
            model.date_joined = dto.date_joined
            model.last_updated = dto.last_updated
        
        for field in ['email', 'first_name', 'last_name', 'phone', 
                     'default_address', 'restaurant_id', 'is_active']:
            value = getattr(dto, field, None)
            if value is not None:
                setattr(model, field, value)
        
        if isinstance(dto, UserCreateDTO) and dto.password:
            model.set_password(dto.password)
        
        return model
