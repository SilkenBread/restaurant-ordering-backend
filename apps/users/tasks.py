import csv
import io
from celery import shared_task
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from apps.restaurants.models import Restaurant
from apps.users.models import User
from django.db import transaction
# from apps.users.services.user_service import UserService

@shared_task(bind=True, max_retries=3)
def process_bulk_users(self, file_content, task_id):
    """
    Procesa un archivo CSV para creación masiva de usuarios
    Args:
        file_content (str): Contenido del archivo CSV
        task_id (str): ID de la tarea para seguimiento
    Returns:
        dict: Resultado del procesamiento
    """    
    # service = UserService()
    results = {
        'task_id': task_id,
        'total': 0,
        'success': 0,
        'errors': [],
        'details': []
    }

    try:
        file = io.StringIO(file_content)
        reader = csv.DictReader(file, delimiter=';')
        rows = list(reader)
        
        if len(rows) > 20:
            results['errors'].append({
                'line': 0,
                'error': _("Límite de 20 usuarios por tarea excedido")
            })
            cache.set(f'bulk_user_task_{task_id}', results, timeout=3600)
            return results
        
        results['total'] = len(rows)
        
        # Validar campos requeridos
        required_fields = {'email', 'password', 'first_name', 'last_name', 'phone'}
        for field in required_fields:
            if field not in reader.fieldnames:
                raise ValidationError(
                    _("El archivo CSV no tiene el formato correcto. Falta el campo: {}").format(field))
        
        existing_emails = set(User.objects.values_list("email", flat=True))
        valid_restaurant_ids = set(Restaurant.objects.values_list("id", flat=True))
        
        valid_users = []
        
        with transaction.atomic():
            for i, row in enumerate(rows, 1):
                try:
                    # Preparar datos del usuario
                    user_data = {
                        'email': row['email'].strip(),
                        'password': row['password'],
                        'first_name': row['first_name'].strip(),
                        'last_name': row['last_name'].strip(),
                        'phone': row['phone'].strip(),
                        'default_address': row.get('default_address', '').strip() or None,
                        'restaurant_id': None,
                    }
                    
                    # Validaciones
                    if not user_data['email']:
                        raise ValidationError(_("El campo email no puede estar vacío"))
                    
                    if user_data['email'] in existing_emails:
                        raise ValidationError(_("El email ya está registrado"))
                    
                    # Procesar restaurant_id si existe
                    if row.get('restaurant_id'):
                        try:
                            restaurant_id = int(row['restaurant_id'])
                            if restaurant_id in valid_restaurant_ids:
                                user_data['restaurant_id'] = restaurant_id
                            else:
                                raise ValidationError(_("El restaurant_id no es válido"))
                        except ValueError:
                            raise ValidationError(_("El restaurant_id debe ser un número entero"))
                    
                    # instancia de usuario
                    user = User(**user_data)
                    user.set_password(user_data['password'])
                    user.full_clean()
                    
                    valid_users.append(user)
                    results['details'].append({
                        'line': i,
                        'email': user_data['email'],
                        'status': 'success'
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    if hasattr(e, 'message_dict'):
                        error_msg = "; ".join(
                            f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()
                        )
                    
                    results['errors'].append({
                        'line': i,
                        'email': row.get('email', ''),
                        'error': error_msg
                    })
                    continue
            
            if valid_users:
                User.objects.bulk_create(valid_users)
                results['success'] = len(valid_users)
        
        cache.set(f'bulk_user_task_{task_id}', results, timeout=3600)
        return results

    except Exception as e:
        error_detail = str(e)
        results['errors'].append({'line': 0, 'error': error_detail})
        cache.set(f'bulk_user_task_{task_id}', results, timeout=3600)
        raise self.retry(exc=e)
