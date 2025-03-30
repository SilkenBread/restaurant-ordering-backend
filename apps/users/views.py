from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from apps.users.dtos.user_create_dto import UserCreateDTO
from apps.users.dtos.user_filter_dto import UserFilterDTO
from apps.users.dtos.user_update_dto import UserUpdateDTO
from apps.users.models import User

from .services.user_service import UserService

from .repositories.user_repository import UserRepository
from .dtos.user_register_dto import UserRegisterDTO

from .serializers import PasswordChangeSerializer, UserCreateSerializer, UserResponseSerializer, UserSerializer, UserUpdateSerializer

class UserViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones CRUD de usuarios
    """
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer 
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService(UserRepository())
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['change_password']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        filter_dto = UserFilterDTO(
            email=request.query_params.get('email'),
            first_name=request.query_params.get('first_name'),
            last_name=request.query_params.get('last_name'),
            phone=request.query_params.get('phone'),
            restaurant_id=request.query_params.get('restaurant_id')
        )

        validation_errors = filter_dto.validate()
        if validation_errors:
            return Response({'errors': validation_errors}, status=status.HTTP_400_BAD_REQUEST)      
        
        # filtrado con django-filters
        filtered_queryset = self.user_service.get_filtered_queryset(request.query_params)
        serializer = UserSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        user = self.user_service.get_user(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_dto = UserCreateDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data.get('last_name', ''),
            phone=serializer.validated_data.get('phone'),
            default_address=serializer.validated_data.get('default_address'),
            restaurant_id=serializer.validated_data.get('restaurant_id')
        )
        
        user, errors = self.user_service.create_user(user_dto)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        response_serializer = UserResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        user = self.user_service.get_user(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_dto = UserUpdateDTO(
            first_name=serializer.validated_data.get('first_name'),
            last_name=serializer.validated_data.get('last_name'),
            phone=serializer.validated_data.get('phone'),
            default_address=serializer.validated_data.get('default_address'),
            is_active=serializer.validated_data.get('is_active'),
            restaurant_id=serializer.validated_data.get('restaurant_id')
        )
        
        updated_user, errors = self.user_service.update_user(pk, user_dto)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        response_serializer = UserResponseSerializer(updated_user)
        return Response(response_serializer.data)
    
    def partial_update(self, request, pk=None):
        user = self.user_service.get_user(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_dto = UserUpdateDTO(
            first_name=serializer.validated_data.get('first_name', user.first_name),
            last_name=serializer.validated_data.get('last_name', user.last_name),
            phone=serializer.validated_data.get('phone', user.phone),
            default_address=serializer.validated_data.get('default_address', user.default_address),
            is_active=serializer.validated_data.get('is_active', user.is_active),
            restaurant_id=serializer.validated_data.get('restaurant_id', user.restaurant_id)
        )
        
        updated_user, errors = self.user_service.update_user(pk, user_dto)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        response_serializer = UserResponseSerializer(updated_user)
        return Response(response_serializer.data)
    
    def destroy(self, request, pk=None):
        success, errors = self.user_service.delete_user(pk)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
