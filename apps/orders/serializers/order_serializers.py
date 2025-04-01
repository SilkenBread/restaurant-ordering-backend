from rest_framework import serializers
from django.utils.translation import gettext as _


class OrderItemDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False)
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S", 
                                          input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"])
    updated_at = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S", 
                                          input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"])

    def validate_quantity(self, value):
        """Validación de cantidad"""
        if value <= 0:
            raise serializers.ValidationError(_("La cantidad debe ser mayor a cero"))
        return value

    def validate_subtotal(self, value):
        """Validación del subtotal"""
        if value <= 0:
            raise serializers.ValidationError(_("El subtotal debe ser mayor a cero"))
        return value


class OrderDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    customer_id = serializers.IntegerField()
    restaurant_id = serializers.IntegerField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_delivery_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S", 
                                                      input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"],
                                                      allow_null=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S", 
                                          input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"])
    updated_at = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S", 
                                          input_formats=["%Y-%m-%d %H:%M:%S", "iso-8601"])
    order_items = OrderItemDTOSerializer(many=True, required=False)

    def validate_status(self, value):
        """Validación del estado"""
        valid_statuses = ["pending", "completed", "cancelled"]
        if value not in valid_statuses:
            raise serializers.ValidationError(_("Estado inválido. Debe ser uno de: pending, completed, cancelled"))
        return value

    def validate_total_amount(self, value):
        """Validación del monto total"""
        if value <= 0:
            raise serializers.ValidationError(_("El monto total debe ser mayor a cero"))
        return value


class OrderCreateDTOSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    restaurant_id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_delivery_time = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        min_length=1
    )

    def validate_items(self, value):
        """Validación de la lista de ítems"""
        if not value:
            raise serializers.ValidationError(_("Se requiere al menos un ítem para crear una orden"))
        
        # validar estructura de cada item
        for item in value:
            if not all(k in item for k in ('menu_item_id', 'quantity', 'subtotal')):
                raise serializers.ValidationError(_("Cada ítem debe contener menu_item_id, quantity y subtotal"))
            
            if item['quantity'] <= 0:
                raise serializers.ValidationError(_("La cantidad debe ser mayor a cero"))
            
            if float(item['subtotal']) <= 0:
                raise serializers.ValidationError(_("El subtotal debe ser mayor a cero"))
        return value


class OrderUpdateDTOSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, allow_null=True)
    delivery_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    special_instructions = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_delivery_time = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    
    def validate_status(self, value):
        """Validación del estado si se proporciona"""
        if value:
            valid_statuses = ["pending", "completed", "cancelled"]
            if value not in valid_statuses:
                raise serializers.ValidationError(_("Estado inválido. Debe ser uno de: pending, completed, cancelled"))
        return value
