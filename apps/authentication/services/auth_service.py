from django.contrib.auth import authenticate
from apps.authentication.dtos.login_dto import LoginDTO
from apps.authentication.dtos.password_change_dto import PasswordChangeDTO
from apps.authentication.dtos.token_dto import TokenDTO
from apps.core.exceptions import UnauthorizedException, ValidationException
from apps.users.repositories.user_repository import UserRepository
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache
from django.utils.translation import gettext as _

class AuthService:
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()

    def login(self, login_dto: LoginDTO) -> TokenDTO:
        """Autentica un usuario y retorna tokens JWT"""
        errors = login_dto.validate()
        if errors:
            raise ValidationException(_("Datos inválidos"), errors)
        
        user = authenticate(
            email=login_dto.email,
            password=login_dto.password
        )
        
        if not user:
            raise UnauthorizedException(_("Credenciales inválidas"))
        
        refresh = RefreshToken.for_user(user)
        return TokenDTO(
            access=str(refresh.access_token),
            refresh=str(refresh)
        )
    
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

    def change_password(self, user, password_dto: PasswordChangeDTO) -> None:
        """Cambia la contraseña de un usuario"""
        errors = password_dto.validate()
        if errors:
            raise ValidationException(_("Datos inválidos"), errors)
        
        if not user.check_password(password_dto.old_password):
            raise UnauthorizedException(_("Contraseña actual incorrecta"))
        
        user.set_password(password_dto.new_password)
        user.save()

        # Limpiar cache del usuario
        cache.delete_pattern(f'user_email_{user.email}')
        cache.delete_pattern(f'user_{user.id}')
