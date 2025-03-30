from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..dtos.login_dto import LoginDTO
from ..dtos.password_change_dto import PasswordChangeDTO
from ..serializers.token_serializer import TokenSerializer
from ..services.auth_service import AuthService
from apps.core.exceptions import UnauthorizedException, ValidationException
from django.utils.translation import gettext_lazy as _

class LoginAPIView(APIView):
    """"
    API para iniciar sesión"
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            login_dto = LoginDTO(**request.data)
            auth_service = AuthService()
            tokens = auth_service.login(login_dto)

            return Response(TokenSerializer(tokens).data, status=status.HTTP_200_OK)
        except ValidationException as e:
            return Response(
                {'error': str(e), 'details': e.details},
                status=status.HTTP_400_BAD_REQUEST
            )
        except UnauthorizedException:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        success = AuthService().logout(refresh_token)
        if not success:
            return Response(
            {'error': 'Token inválido o ya revocado'},
            status=status.HTTP_400_BAD_REQUEST
        )
        return Response(
            {'message': 'Cierrado de sesión exitoso'},
            status=status.HTTP_200_OK
        )
        
class PasswordChangeAPIView(APIView):
    def post(self, request):
        try:
            password_dto = PasswordChangeDTO(**request.data)
            AuthService().change_password(request.user, password_dto)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except ValidationException as e:
            return Response({
                "status": "error",
                "code": "validation_error",
                "message": e.detail,
                "errors": e.errors
            }, status=e.status_code)
            
        except UnauthorizedException as e:
            return Response({
                "status": "error",
                "code": "unauthorized",
                "message": str(e),
                "errors": {
                    "old_password": [str(e)]
                }
            }, status=e.status_code)
            
        except Exception as e:
            return Response({
                "status": "error",
                "code": "server_error",
                "message": _("Error interno del servidor"),
                "errors": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
