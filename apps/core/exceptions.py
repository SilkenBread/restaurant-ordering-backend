from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

class ValidationException(APIException):
    status_code = 400
    default_detail = _("Error de validación.")
    default_code = "validation_error"

    def __init__(self, detail=None, errors=None):
        if detail is None:
            detail = self.default_detail
        self.errors = errors
        super().__init__({"detail": detail, "errors": errors})
