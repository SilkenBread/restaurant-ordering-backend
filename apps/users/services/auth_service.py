from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from ..dtos.user_login_dto import UserLoginDTO
from ..dtos.user_response_dto import UserResponseDTO
from ..dtos.user_register_dto import UserRegisterDTO
from ..repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def login(self, login_dto: UserLoginDTO) -> tuple[UserResponseDTO, bool]:
        user = self.repository.get_by_email(login_dto.email)
        if not user or not user.check_password(login_dto.password) or not user.is_active:
            return None, False
        
        refresh = RefreshToken.for_user(user)
        response_dto = UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )
        return response_dto, True
    
    def register(self, register_dto: UserRegisterDTO) -> tuple[UserResponseDTO, dict]:
        validation_errors = register_dto.validate()
        if validation_errors:
            return None, validation_errors
        
        if self.repository.get_by_email(register_dto.email):
            return None, {'email': 'Ya existe un usuario con este correo'}
        
        user_data = {
            'email': register_dto.email,
            'password': register_dto.password,
            'first_name': register_dto.first_name,
            'last_name': register_dto.last_name,
            'phone': register_dto.phone,
            'default_address': register_dto.default_address
        }
        
        if register_dto.restaurant_id:
            user_data['restaurant_id'] = register_dto.restaurant_id
        
        user = self.repository.create(user_data)
        
        refresh = RefreshToken.for_user(user)
        response_dto = UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            access=str(refresh.access_token),
            refresh=str(refresh)
        )
        return response_dto, None
    
    def logout(self, refresh_token: str) -> bool:
        """
        Invalida el token refresh para logout
        Returns:
            bool: True si el logout fue exitoso, False si el token era inválido
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except TokenError:
            return False
