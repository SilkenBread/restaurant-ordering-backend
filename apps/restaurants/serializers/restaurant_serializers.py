from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

@extend_schema_serializer(
    component_name="Restaurant",
    examples=[]
)
class RestaurantDTOSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField()
    address = serializers.CharField()
    rating = serializers.FloatField()
    status = serializers.CharField()
    category = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

@extend_schema_serializer(
    component_name="RestaurantList",
)
class RestaurantListDTOSerializer(serializers.Serializer):
    items = RestaurantDTOSerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
