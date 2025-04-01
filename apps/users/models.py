from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError(_('El correo electrónico es obligatorio'))
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser debe tener is_superuser=True.'))

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('Correo Electrónico'),
        max_length=255,
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este correo electrónico.'),
        },
    )
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellido'), max_length=100)
    phone = models.CharField(_('Teléfono'), max_length=20, blank=True, null=True)
    default_address = models.TextField(_('Dirección por defecto'), blank=True, null=True)

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Restaurant')
    )
    
    is_staff = models.BooleanField(
        _('Acceso a admin'),
        default=False,
        help_text=_('Determina si el usuario puede acceder al sitio de administración.'),
    )
    is_superuser = models.BooleanField(
        _('Superusuario'),
        default=False,
        help_text=_('Determina si el usuario tiene todos los permisos sin asignarlos explícitamente.'),
    )
    is_active = models.BooleanField(
        _('Activo'),
        default=True,
        help_text=_(
            'Desmarque esta opción en lugar de eliminar el usuario.'
        ),
    )
    date_joined = models.DateTimeField(_('Fecha de registro'), auto_now_add=True)
    last_updated = models.DateTimeField(_('Última actualización'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    class Meta:
        db_table = 'USERS'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name
