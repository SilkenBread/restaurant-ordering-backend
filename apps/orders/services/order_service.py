from typing import Optional, Dict, Any, Union
from django.db import models, transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import NotFound, ValidationError

from ..repositories import OrderRepository, OrderItemRepository
from ..dtos import OrderDTO, OrderCreateDTO, OrderUpdateDTO, OrderItemDTO
from ..models import Order, OrderItem
from ..serializers import (
    OrderDTOSerializer, 
    OrderCreateDTOSerializer,
    OrderUpdateDTOSerializer
)
from ..filters import OrderFilter
from apps.core.exceptions import ValidationException


class OrderService:
    def __init__(self, order_repository: OrderRepository = None, 
                order_item_repository: OrderItemRepository = None):
        self.order_repository = order_repository or OrderRepository()
        self.order_item_repository = order_item_repository or OrderItemRepository()
    
    def _format_validation_error(self, serializer_errors):
        """Formatea errores de validación para una respuesta consistente"""
        return {
            "status": "error",
            "code": "validation_error",
            "message": _("Error de validación en los datos proporcionados"),
            "errors": serializer_errors
        }
    
    def get_order(self, order_id: int) -> Optional[OrderDTO]:
        """Obtiene una orden por su ID"""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFound(_("Orden no encontrada"))
        
        # Convertir a DTO
        return self._to_dto(order)
    
    def list_orders(self, filters: Optional[Dict[str, Any]] = None) -> models.QuerySet:
        """Lista órdenes con filtros opcionales"""
        base_queryset = self.order_repository.get_all()
        
        # Aplicar filtros
        filter_set = OrderFilter(filters or {}, queryset=base_queryset)
        filtered_queryset = filter_set.qs
        
        return filtered_queryset.order_by('-created_at')
    
    @transaction.atomic
    def create_order(self, order_data: OrderCreateDTO) -> Dict:
        """Crea una nueva orden con sus ítems"""
        try:
            # Validar datos de entrada
            serializer = OrderCreateDTOSerializer(data=order_data.__dict__)
            serializer.is_valid(raise_exception=True)
            
            # Crear orden en estado "pending"
            order = Order(
                customer_id=order_data.customer_id,
                restaurant_id=order_data.restaurant_id,
                status="pending",
                total_amount=order_data.total_amount,
                delivery_address=order_data.delivery_address,
                special_instructions=order_data.special_instructions,
                estimated_delivery_time=order_data.estimated_delivery_time,
                is_active=order_data.is_active
            )
            
            # Crear la orden
            created_order = self.order_repository.create(order)
            
            # Crear los ítems de la orden
            order_items = []
            for item_data in order_data.items:
                order_item = OrderItem(
                    order=created_order,
                    menu_item_id=item_data['menu_item_id'],
                    quantity=item_data['quantity'],
                    subtotal=item_data['subtotal'],
                    note=item_data.get('note', None),
                    is_active=True
                )
                order_items.append(order_item)
            
            # Crear los ítems en batch para optimizar
            self.order_item_repository.create_batch(order_items)
            
            # Recargar la orden con sus ítems para devolver
            complete_order = self.order_repository.get_by_id(created_order.id)
            return OrderDTOSerializer(self._to_dto(complete_order)).data
            
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
    def update_order(self, order_id: int, order_data: Dict) -> Dict:
        """Actualiza una orden existente"""
        try:
            # Verificar que la orden exista
            existing = self.order_repository.get_by_id(order_id)
            if not existing:
                raise NotFound(detail={
                    "status": "error",
                    "code": "not_found",
                    "message": _("Orden no encontrada")
                })
            
            # Validar datos de actualización
            serializer = OrderUpdateDTOSerializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar si hay campos para actualizar
            if not serializer.validated_data:
                return {
                    "status": "success",
                    "code": "no_changes",
                    "message": _("No se proporcionaron campos para actualizar"),
                    "data": OrderDTOSerializer(self._to_dto(existing)).data
                }
            
            # Actualizar campos
            for field, value in serializer.validated_data.items():
                if value is not None:
                    setattr(existing, field, value)
            
            # Guardar cambios
            updated_order = self.order_repository.update(existing)
            
            return OrderDTOSerializer(self._to_dto(updated_order)).data
            
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
    
    @transaction.atomic
    def delete_order(self, order_id: int) -> bool:
        """Elimina (marca como inactiva) una orden"""
        # Primero verificamos que exista
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return False
        
        # Marcamos como inactivos los ítems asociados
        self.order_item_repository.delete_by_order_id(order_id)
        
        # Marcamos como inactiva la orden
        return self.order_repository.delete(order_id)
    
    def _to_dto(self, model: Order) -> OrderDTO:
        """Convierte un modelo Order a su DTO"""
        # Convertir items a DTOs
        item_dtos = None
        if hasattr(model, 'order_items'):
            item_dtos = [
                OrderItemDTO(
                    id=item.id,
                    order_id=item.order_id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    subtotal=float(item.subtotal),
                    note=item.note,
                    is_active=item.is_active,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                ) for item in model.order_items.all() if item.is_active
            ]
        
        # Crear DTO de la orden
        return OrderDTO(
            id=model.id,
            customer_id=model.customer_id,
            restaurant_id=model.restaurant_id,
            status=model.status,
            total_amount=float(model.total_amount),
            delivery_address=model.delivery_address,
            special_instructions=model.special_instructions,
            estimated_delivery_time=model.estimated_delivery_time,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            order_items=item_dtos
        )
    
    def _to_model(self, dto: Union[OrderCreateDTO, OrderUpdateDTO, OrderDTO]) -> Order:
        """Convierte un DTO a modelo Order"""
        model = Order()
        
        if isinstance(dto, OrderDTO) and dto.id:
            model.id = dto.id
        
        for field in ['customer_id', 'restaurant_id', 'status', 'total_amount', 
                     'delivery_address', 'special_instructions', 
                     'estimated_delivery_time', 'is_active']:
            value = getattr(dto, field, None)
            if value is not None:
                setattr(model, field, value)
        
        return model
