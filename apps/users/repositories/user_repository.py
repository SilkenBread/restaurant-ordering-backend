from typing import Optional
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from ..models import User
from .interfaces import IUserRepository

class UserRepository(IUserRepository):
    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
        
    def get_all(self) -> list[User]:
        return User.objects.filter(is_active=True).all()

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
        
    def create(self, user_data: dict) -> User:
        user_data['password'] = make_password(user_data['password'])
        return User.objects.create(**user_data)
    
    def update(self, user: User, user_data: dict) -> User:
        for field, value in user_data.items():
            setattr(user, field, value)
        user.save()
        return user
    
    def delete(self, user: User) -> None:
        user.is_active = False
        user.save()

    def filter(self, filters: dict, queryset=None) -> list[User]:
        if queryset is None:
            queryset = User.objects.filter(is_active=True)
        
        if filters:
            queryset = queryset.filter(**filters)
        
        return queryset.all()
    
    def update_password(self, user: User, new_password: str) -> User:
        """Actualiza la contraseña del usuario"""
        user.password = make_password(new_password)
        user.save()
        return user
