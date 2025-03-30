from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework import status

class ValidationException(APIException):
    status_code = 400
    default_detail = _("Error de validación.")
    default_code = "validation_error"

    def __init__(self, detail=None, errors=None):
        if detail is None:
            detail = self.default_detail
        self.errors = errors
        super().__init__({"detail": detail, "errors": errors})

class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Credenciales inválidas.")
    default_code = "unauthorized"
