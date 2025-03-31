from typing import Dict, Optional, Any, Union
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, ValidationError

from apps.menu.dtos.menuitem_dtos import MenuItemCreateDTO, MenuItemDTO, MenuItemUpdateDTO
from apps.menu.filters.menuitem_filters import MenuItemFilter
from apps.menu.repositories.menuitem_repository import MenuItemRepository
from apps.menu.serializers.menuitem_serializer import MenuItemCreateDTOSerializer, MenuItemDTOSerializer, MenuItemUpdateDTOSerializer
from ..models import MenuItem
from rest_framework import serializers

class MenuItemService:
    def __init__(self, repository: MenuItemRepository = None):
        self.repository = repository or MenuItemRepository()
    
    def _format_validation_error(self, serializer_errors):
        return {
            "status": "error",
            "code": "validation_error",
            "message": _("Error de validación en los datos proporcionados"),
            "errors": serializer_errors
        }
    
    def get_menu_item(self, menu_item_id: int) -> Optional[MenuItemDTO]:
        menu_item = self.repository.get_by_id(menu_item_id)
        if not menu_item:
            raise NotFound(detail={
                "status": "error",
                "code": "not_found",
                "message": _("Ítem de menú no encontrado")
            })
        return self._to_dto(menu_item)
    
    def list_menu_items(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        try:
            base_queryset = self.repository.get_all()
            filter_set = MenuItemFilter(filters or {}, queryset=base_queryset)
            return filter_set.qs.order_by('-created_at')
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "filter_error",
                "message": str(e)
            })
    
    def create_menu_item(self, menu_item_data: Dict, image_file=None) -> Dict:
        try:
            # Si hay un archivo de imagen, asignarlo a los datos
            if image_file:
                menu_item_data['image'] = image_file
            
            serializer = MenuItemCreateDTOSerializer(data=menu_item_data)
            serializer.is_valid(raise_exception=True)
            
            # Crear el objeto MenuItem
            menu_item = self._to_model(MenuItemCreateDTO(**serializer.validated_data))
            created = self.repository.create(menu_item)
            
            # Preparar la respuesta
            dto = self._to_dto(created)
            return MenuItemDTOSerializer(dto, context={'request': getattr(image_file, '_request', None)}).data
            
        except serializers.ValidationError as e:
            raise ValidationError(detail=self._format_validation_error(e.detail))
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "create_error",
                "message": str(e)
            })
    
    def update_menu_item(self, menu_item_id: int, menu_item_data: Dict, image_file=None) -> Dict:
        try:
            existing = self.repository.get_by_id(menu_item_id)
            if not existing:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Ítem de menú no encontrado")
                })
            
            # Si hay un archivo de imagen, asignarlo a los datos
            if image_file:
                menu_item_data['image'] = image_file
            
            serializer = MenuItemUpdateDTOSerializer(data=menu_item_data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar campos para actualizar
            if not serializer.validated_data:
                return {
                    "status": "success",
                    "code": "no_changes",
                    "message": _("No se proporcionaron campos para actualizar"),
                    "data": MenuItemDTOSerializer(
                        self._to_dto(existing), 
                        context={'request': getattr(image_file, '_request', None)}
                    ).data
                }
            
            # Manejar caso especial cuando se quiere eliminar la imagen
            if 'image' in menu_item_data and menu_item_data['image'] is None:
                if existing.image:
                    # Eliminar la imagen existente
                    existing.image.delete(save=False)
                    existing.image = None
            
            # Actualizar campos
            for field, value in serializer.validated_data.items():
                if value is not None:  # Solo actualizar si el valor no es None
                    setattr(existing, field, value)
            
            updated = self.repository.update(existing)
            return MenuItemDTOSerializer(
                self._to_dto(updated), 
                context={'request': getattr(image_file, '_request', None)}
            ).data
            
        except serializers.ValidationError as e:
            raise ValidationError(detail=self._format_validation_error(e.detail))
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "update_error",
                "message": str(e)
            })
    
    def delete_menu_item(self, menu_item_id: int) -> bool:
        try:
            deleted = self.repository.delete(menu_item_id)
            if not deleted:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Ítem de menú no encontrado")
                })
            return deleted
        except Exception as e:
            raise ValidationError(detail={
                "status": "error",
                "code": "delete_error",
                "message": str(e)
            })
    
    def _to_dto(self, model: MenuItem) -> MenuItemDTO:
        return MenuItemDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            preparation_time=model.preparation_time,
            category=model.category,
            restaurant_id=model.restaurant.id if model.restaurant else None,
            is_active=model.is_active,
            is_available=model.is_available,
            created_at=model.created_at,
            updated_at=model.updated_at,
            image=model.image.url if model.image else None
        )
    
    def _to_model(self, dto: Union[MenuItemCreateDTO, MenuItemUpdateDTO, MenuItemDTO]) -> MenuItem:
        if isinstance(dto, MenuItemDTO) and dto.id:
            # Si el DTO tiene ID, intentamos obtener el modelo existente
            model = self.repository.get_by_id(dto.id)
            if not model:
                model = MenuItem()
        else:
            model = MenuItem()
        
        # Transferir datos del DTO al modelo
        fields_to_update = ['name', 'description', 'price', 'preparation_time', 
                           'category', 'is_active', 'is_available', 'image']
        
        for field in fields_to_update:
            value = getattr(dto, field, None)
            if value is not None:
                setattr(model, field, value)
        
        # Manejar la relación ForeignKey
        if hasattr(dto, 'restaurant_id') and dto.restaurant_id is not None:
            model.restaurant_id = dto.restaurant_id
        
        return model
