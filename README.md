# restaurant-ordering-backend
Restaurant Order Management System


# Si se cambia el `models.py`
```sh
docker-compose run --rm django python manage.py makemigrations
```
```sh
docker-compose run --rm django python manage.py migrate
```