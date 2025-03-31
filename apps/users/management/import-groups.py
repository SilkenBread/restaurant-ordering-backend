from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.orders.models import Order
from menu.models import MenuItem

class Command(BaseCommand):
    help = "Crea los grupos Customer y Dealer con permisos asociados."

    PERMISSION_NAMES = {
        "en": {
            "add": "Can add {model}",
            "change": "Can change {model}",
            "delete": "Can delete {model}",
            "view": "Can view {model}",
        },
        "es": {
            "add": "Puede agregar {model}",
            "change": "Puede cambiar {model}",
            "delete": "Puede eliminar {model}",
            "view": "Puede ver {model}",
        },
    }

    MODELS = [Restaurant, User, Order, MenuItem]

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            type=str,
            choices=["en", "es"],
            default="en",
            help="Idioma para los nombres de los permisos (en o es).",
        )

    def handle(self, *args, **kwargs):
        lang = kwargs["lang"]
        self.stdout.write(f"Usando idioma: {lang}")

        # Crear grupos
        for group_name in ["Customer", "Dealer"]:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Grupo '{group_name}' creado."))
            else:
                self.stdout.write(self.style.WARNING(f"Grupo '{group_name}' ya existe."))

            # Asociar permisos a cada grupo
            for model in self.MODELS:
                content_type = ContentType.objects.get_for_model(model)
                for action, perm_name in self.PERMISSION_NAMES[lang].items():
                    perm_codename = f"{action}_{model._meta.model_name}"
                    permission = Permission.objects.filter(
                        codename=perm_codename, content_type=content_type
                    ).first()
                    if permission:
                        group.permissions.add(permission)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Permiso '{perm_name.format(model=model._meta.verbose_name)}' asignado a '{group_name}'."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"No se encontró el permiso '{perm_codename}' para {model._meta.verbose_name}."
                            )
                        )
        
        self.stdout.write(self.style.SUCCESS("Importación de grupos completada."))
