from functools import wraps
from rest_framework.exceptions import PermissionDenied

def permission_required(perms):
    """
    Decorador para asignar permisos a métodos de vista
    Ejemplo de uso:
    @permission_required(['restaurants.view_restaurant'])
    def get(self, request):
        ...
    """
    def decorator(view_method):
        @wraps(view_method)
        def wrapped_view(self, request, *args, **kwargs):
            # Verificar permisos
            for perm in perms:
                if not request.user.has_perm(perm):
                    raise PermissionDenied(
                        detail="No tiene permiso para esta acción.",
                        code='permission_denied'
                    )
            return view_method(self, request, *args, **kwargs)
        return wrapped_view
    return decorator
