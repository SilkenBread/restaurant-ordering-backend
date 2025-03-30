from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework import status

class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Error de validación.")
    default_code = "validation_error"

    def __init__(self, detail=None, errors=None):
        self.detail = self._prepare_detail(detail)
        self.errors = self._prepare_errors(errors)
        super().__init__(detail=self.detail)

    def _prepare_detail(self, detail):
        if detail is None:
            return self.default_detail
        if isinstance(detail, dict) and 'detail' in detail:
            return str(detail['detail'])
        return str(detail)

    def _prepare_errors(self, errors):
        if not errors:
            return {}
        
        clean_errors = {}
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                clean_errors[field] = [str(err) for err in error_list]
            else:
                clean_errors[field] = [str(error_list)]
        
        return clean_errors

class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Credenciales inválidas.")
    default_code = "unauthorized"
