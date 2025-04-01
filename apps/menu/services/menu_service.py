from typing import Optional, Dict, Any, List, Union
from django.db import models, transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import NotFound, ValidationError

from ..repositories import MenuItemRepository
from ..dtos import MenuItemDTO, MenuItemCreateDTO, MenuItemUpdateDTO
from ..models import MenuItem
from ..serializers import (
    MenuItemDTOSerializer, 
    MenuItemCreateDTOSerializer,
    MenuItemUpdateDTOSerializer
)
from ..filters import MenuItemFilter

from apps.core.exceptions import ValidationException


class MenuService:
    def __init__(self, repository: MenuItemRepository = None):
        self.repository = repository or MenuItemRepository()
    
    def _format_validation_error(self, serializer_errors):
        """Formatea errores de validación para una respuesta consistente"""
        return {
            "status": "error",
            "code": "validation_error",
            "message": _("Error de validación en los datos proporcionados"),
            "errors": serializer_errors
        }
    
    def get_menu_item(self, menu_item_id: int) -> Optional[MenuItemDTO]:
        """Obtiene un ítem de menú por su ID"""
        menu_item = self.repository.get_by_id(menu_item_id)
        if not menu_item:
            raise NotFound(_("Ítem de menú no encontrado"))
        
        # Convertir a DTO
        return self._to_dto(menu_item)
    
    def list_menu_items(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        """Lista ítems de menú con filtros opcionales"""
        base_queryset = self.repository.get_all()
        
        # Aplicar filtros
        filter_set = MenuItemFilter(filters or {}, queryset=base_queryset)
        filtered_queryset = filter_set.qs
        
        return filtered_queryset.order_by('category', 'name')
    
    def get_restaurant_menu(self, restaurant_id: int) -> List[MenuItemDTO]:
        """Obtiene todos los ítems de menú de un restaurante específico"""
        items = self.repository.get_by_restaurant_id(restaurant_id)
        return [self._to_dto(item) for item in items]
    
    @transaction.atomic
    def create_menu_item(self, menu_item_data: MenuItemCreateDTO) -> Dict:
        """Crea un nuevo ítem de menú"""
        try:
            # Validar datos de entrada
            serializer = MenuItemCreateDTOSerializer(data=menu_item_data.__dict__)
            serializer.is_valid(raise_exception=True)
            
            # Crear ítem de menú
            menu_item = self._to_model(menu_item_data)
            created_item = self.repository.create(menu_item)
            
            # Retornar DTO serializado
            return MenuItemDTOSerializer(self._to_dto(created_item)).data
            
        except ValidationError as e:
            # Centralizar manejo de errores de validación
            raise ValidationException(detail=self._format_validation_error(e.detail))
        except Exception as e:
            # Centralizar manejo de errores generales
            raise ValidationException(detail={
                "status": "error",
                "code": "create_error",
                "message": str(e)
            })
    
    @transaction.atomic
    def update_menu_item(self, menu_item_id: int, menu_item_data: Dict) -> Dict:
        """Actualiza un ítem de menú existente"""
        try:
            # Verificar que el ítem exista
            existing = self.repository.get_by_id(menu_item_id)
            if not existing:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Ítem de menú no encontrado")
                })
            
            # Validar datos de actualización
            serializer = MenuItemUpdateDTOSerializer(data=menu_item_data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar si hay campos para actualizar
            if not serializer.validated_data:
                return {
                    "status": "success",
                    "code": "no_changes",
                    "message": _("No se proporcionaron campos para actualizar"),
                    "data": MenuItemDTOSerializer(self._to_dto(existing)).data
                }
            
            # Actualizar campos
            for field, value in serializer.validated_data.items():
                if value is not None:
                    setattr(existing, field, value)
            
            # Guardar cambios
            updated_item = self.repository.update(existing)
            
            return MenuItemDTOSerializer(self._to_dto(updated_item)).data
            
        except ValidationError as e:
            raise ValidationException(detail=self._format_validation_error(e.detail))
        except NotFound as e:
            raise e
        except Exception as e:
            raise ValidationException(detail={
                "status": "error",
                "code": "update_error",
                "message": str(e)
            })
    
    def delete_menu_item(self, menu_item_id: int) -> bool:
        """Elimina (marca como inactivo) un ítem de menú"""
        return self.repository.delete(menu_item_id)
    
    def _to_dto(self, model: MenuItem) -> MenuItemDTO:
        """Convierte un modelo MenuItem a su DTO"""
        return MenuItemDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            price=float(model.price),
            preparation_time=model.preparation_time,
            category=model.category,
            restaurant_id=model.restaurant_id,
            is_active=model.is_active,
            is_available=model.is_available,
            image=model.image.url if model.image else None,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, dto: Union[MenuItemCreateDTO, MenuItemUpdateDTO, MenuItemDTO]) -> MenuItem:
        """Convierte un DTO a modelo MenuItem"""
        model = MenuItem()
        
        if isinstance(dto, MenuItemDTO) and dto.id:
            model.id = dto.id
        
        for field in ['name', 'description', 'price', 'preparation_time', 
                     'category', 'restaurant_id', 'is_active', 'is_available', 'image']:
            if hasattr(dto, field):
                value = getattr(dto, field, None)
                if value is not None:
                    setattr(model, field, value)
        
        return model
