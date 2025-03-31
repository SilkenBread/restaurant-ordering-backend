# restaurant-ordering-backend
Restaurant Order Management System

## Iniciar Proyecto
> **Recomendacion** Se recomienda crear un entorno virtual .venv en local e instalar `requirements.txt`
Una vez clonado el repositorio, se debe crear un archivo .env para las credenciales a la Base de Datos PostgreSQL
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT= 
# Zona horaria
TZ=America/Bogota
```

## Comandos Para iniciar
> Todos los comandos inician con `docker compose run --rm django` para iniciar una instancia del contenedor, puede acceder al contenedor para ejecutarlo internamente
Se debe ingresar el siguiente comando personalizado para importar los grupos (dealer, customer) con sus respectivos permisos asociados
```sh
docker compose run --rm django python manage.py import-groups
```

### Contruir proyecto
```sh
docker compose build
```
Una vez contruido y levantado todos los servicios, debemos crear las tablas en nuestra base de datos, por lo que debemos ejecutar
```sh
docker compose run --rm django python manage.py mgrate
```

Ahora si estamos listos para levantar nuestra aplicación
```sh
docker compose up
```

## Si se cambia el `models.py`
```sh
docker-compose run --rm django python manage.py makemigrations
```
```sh
docker-compose run --rm django python manage.py migrate
```

## Ejecutar Test
```sh
# Ejecutar TODOS los tests
python manage.py test apps.restaurants

# Ejecutar solo tests unitarios
python manage.py test apps.restaurants.tests

# Ejecutar solo tests de integración
python manage.py test apps.restaurants.tests.integration

# Ejecutar tests específicos
python manage.py test apps.restaurants.tests.test_services.RestaurantServiceTests
```
