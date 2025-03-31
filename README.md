# Restaurant Ordering Backend

Sistema de gestión de pedidos para restaurantes.

## 📌 Requisitos Previos

Se recomienda crear un entorno virtual `.venv` en local e instalar las dependencias desde `requirements.txt`.

## 📂 Configuración del Entorno

Antes de iniciar el proyecto, es necesario configurar las credenciales de la base de datos PostgreSQL en un archivo `.env` dentro del proyecto:

```.env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

# Zona horaria
TZ=America/Bogota
```

## 🚀 Instalación y Ejecución

### 1️⃣ Construir la imagen Docker
```sh
docker compose build
```

### 2️⃣ Crear las tablas en la base de datos
```sh
docker compose run --rm django python manage.py migrate
```

### 3️⃣ Iniciar la aplicación
```sh
docker compose up
```

## 🔄 Migraciones de Modelos

Si se realizan cambios en `models.py`, ejecutar:

```sh
docker compose run --rm django python manage.py makemigrations
```
```sh
docker compose run --rm django python manage.py migrate
```

## 📥 Importación de Datos

### 🔹 Comando `import_groups`
Este comando carga los grupos y sus permisos desde un archivo CSV ubicado en `data/groups_permissions.csv`.

#### 📄 Formato del archivo CSV
Cada fila debe seguir la estructura:
```csv
grupo;modelo;ver;crear;actualizar;eliminar
```
Ejemplo:
```csv
Customer;restaurant;1;0;0;0
Dealer;order;1;1;1;1
```

### 🔹 Comando `import_restaurants`
_(Pendiente de documentación)_

## ✅ Ejecutar Tests

Para ejecutar las pruebas, usa los siguientes comandos:

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