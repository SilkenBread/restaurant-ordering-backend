import os
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = "Carga los grupos y permisos desde un archivo CSV ubicado en 'import/groups_permissions.csv'."

    CSV_PATH = "import/groups_permissions.csv"

    def handle(self, *args, **kwargs):
        if not os.path.exists(self.CSV_PATH):
            self.stdout.write(self.style.ERROR(f"No se encontró el archivo: {self.CSV_PATH}"))
            return
        
        with open(self.CSV_PATH, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            
            for row in reader:
                group_name = row["grupo"]
                model_name = row["modelo"]
                permissions_map = {
                    "ver": "view",
                    "crear": "add",
                    "actualizar": "change",
                    "eliminar": "delete"
                }

                # Obtener o crear grupo
                group, created = Group.objects.get_or_create(name=group_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Grupo '{group_name}' creado."))

                # Buscar modelo en todas las apps
                model = None
                for app_config in apps.get_app_configs():
                    try:
                        model = app_config.get_model(model_name)
                        break
                    except LookupError:
                        continue

                if not model:
                    self.stdout.write(self.style.ERROR(f"Modelo '{model_name}' no encontrado."))
                    continue

                content_type = ContentType.objects.get_for_model(model)
                model_db_name = content_type.model

                # Asignar permisos al grupo
                for action, codename_prefix in permissions_map.items():
                    if row[action] == "1":
                        codename = f"{codename_prefix}_{model_db_name}"
                        permission = Permission.objects.filter(codename=codename).first()

                        if permission:
                            group.permissions.add(permission)
                            self.stdout.write(self.style.SUCCESS(f"Permiso '{codename}' asignado a '{group_name}'."))  
                        else:
                            self.stdout.write(self.style.ERROR(f"Permiso '{codename}' no encontrado."))

        self.stdout.write(self.style.SUCCESS("Importación de grupos y permisos completada."))
