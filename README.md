# restaurant-ordering-backend
Restaurant Order Management System


# Si se cambia el `models.py`
```sh
docker-compose run --rm django python manage.py makemigrations
```
```sh
docker-compose run --rm django python manage.py migrate
```

```sh
# Ejecutar TODOS los tests (Django-style)
python manage.py test apps.restaurants

# Ejecutar solo tests unitarios
python manage.py test apps.restaurants.tests

# Ejecutar solo tests de integración
python manage.py test apps.restaurants.tests.integration

# Ejecutar tests específicos
python manage.py test apps.restaurants.tests.test_services.RestaurantServiceTests
```