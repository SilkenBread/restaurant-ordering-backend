from functools import wraps
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

def permission_required(perms):
    def decorator(view_method):
        @wraps(view_method)
        def wrapped_view(self, request, *args, **kwargs):
            # Verifica si el usuario está autenticado
            if not request.user.is_authenticated:
                raise NotAuthenticated()
                
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
