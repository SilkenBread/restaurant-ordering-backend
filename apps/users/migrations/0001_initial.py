# Generated by Django 5.1.6 on 2025-03-29 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(error_messages={'unique': 'Ya existe un usuario con este correo electrónico.'}, max_length=255, unique=True, verbose_name='Correo Electrónico')),
                ('first_name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('last_name', models.CharField(max_length=100, verbose_name='Apellido')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('default_address', models.TextField(blank=True, null=True, verbose_name='Dirección por defecto')),
                ('is_staff', models.BooleanField(default=False, help_text='Determina si el usuario puede acceder al sitio de administración.', verbose_name='Acceso a admin')),
                ('is_superuser', models.BooleanField(default=False, help_text='Determina si el usuario tiene todos los permisos sin asignarlos explícitamente.', verbose_name='Superusuario')),
                ('is_active', models.BooleanField(default=True, help_text='Desmarque esta opción en lugar de eliminar el usuario.', verbose_name='Activo')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'db_table': 'USERS',
                'ordering': ['-date_joined'],
            },
        ),
    ]
