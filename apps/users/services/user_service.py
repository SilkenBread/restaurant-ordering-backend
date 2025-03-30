from typing import List, Tuple, Optional

from apps.users.filters.user_filters import UserFilter

from ..dtos.user_create_dto import UserCreateDTO
from ..dtos.user_filter_dto import UserFilterDTO
from ..dtos.user_update_dto import UserUpdateDTO

from ..repositories.user_repository import UserRepository
from ..dtos.password_change_dto import PasswordChangeDTO
from ..models import User


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.get_by_id(user_id)
    
    def list_users(self) -> List[User]:
        return self.repository.get_all()
    
    def create_user(self, user_dto: UserCreateDTO) -> Tuple[Optional[User], dict]:
        validation_errors = user_dto.validate()
        if validation_errors:
            return None, validation_errors
        
        if self.repository.get_by_email(user_dto.email):
            return None, {'email': 'User with this email already exists'}
        
        user_data = {
            'email': user_dto.email,
            'password': user_dto.password,
            'first_name': user_dto.first_name,
            'last_name': user_dto.last_name,
            'phone': user_dto.phone,
            'default_address': user_dto.default_address
        }
        
        if user_dto.restaurant_id:
            user_data['restaurant_id'] = user_dto.restaurant_id
        
        user = self.repository.create(user_data)
        return user, {}
    
    def update_user(self, user_id: int, user_dto: UserUpdateDTO) -> Tuple[Optional[User], dict]:
        user = self.repository.get_by_id(user_id)
        if not user:
            return None, {'error': 'User not found'}
        
        validation_errors = user_dto.validate()
        if validation_errors:
            return None, validation_errors
        
        if user_dto.email and user_dto.email != user.email:
            if self.repository.get_by_email(user_dto.email):
                return None, {'email': 'Email already in use by another user'}
        
        update_data = {
            'email': user_dto.email,
            'first_name': user_dto.first_name,
            'last_name': user_dto.last_name,
            'phone': user_dto.phone,
            'default_address': user_dto.default_address,
            'is_active': user_dto.is_active
        }
        
        if user_dto.restaurant_id:
            update_data['restaurant_id'] = user_dto.restaurant_id
        
        # Eliminar campos None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        updated_user = self.repository.update(user, update_data)
        return updated_user, {}
    
    def delete_user(self, user_id: int) -> Tuple[bool, dict]:
        user = self.repository.get_by_id(user_id)
        if not user:
            return False, {'error': 'User not found'}
        
        self.repository.delete(user)
        return True, {}
    
    def get_filtered_queryset(self, filters=None, queryset=None) -> List[User]:
        qs = User.objects.filter(is_active=True)
        user_filter = UserFilter(filters, queryset=qs)
        return user_filter.qs
