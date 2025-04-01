# 🍽️ Restaurant Ordering Backend

Sistema de gestión de pedidos para restaurantes.

---

## 📌 Requisitos Previos

Se recomienda crear un entorno virtual `.venv` en local e instalar las dependencias desde `requirements.txt`.

---

## 📂 Configuración del Entorno

Es necesario configurar las credenciales de la base de datos **PostgreSQL** en un archivo `.env` en la raíz:

```ini
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

# Zona horaria
TZ=America/Bogota
```

---

## 🚀 Instalación y Ejecución

### 🔧 1️⃣ Construir Proyecto

Se construirán los contenedores de **Django**, **PostgreSQL**, **Redis** y **Celery**:

```sh
docker compose build
```

### 🛠️ 2️⃣ Crear las tablas en la base de datos

```sh
python manage.py migrate
```

> **IMPORTANTE** Todos los comandos que ejecuten `manage.py` pueden hacerse de forma convencional en el exec, o temporalmente con:
>
> ```sh
> docker compose run --rm django python manage.py <comando>
> ```
>
> donde `django` es el nombre del contenedor del backend.

### 🚦 3️⃣ Iniciar la Aplicación

Puedes iniciar el proyecto de dos formas: desde cero o cargando datos de prueba.

#### 🔹 Inicio desde Cero

1. **Crear un superusuario**

```sh
python manage.py createsuperuser
```

2. **Crear grupos y permisos** Se ha agregado un comando personalizado para crear grupos y asociar permisos desde un archivo `.csv`:
   ```sh
   python manage.py import_groups
   ```
   > 📌 **Ubicación:** `/import/groups_permissions.py` Puedes modificar los permisos en el archivo CSV antes de ejecutar el comando.
   >
   > **Roles Base:**
   >
   > - **Dealer**
   > - **Customer**

   **Ejemplo de estructura del archivo CSV:**
   
   | Grupo   | Modelo    | Ver | Crear | Actualizar | Eliminar |
   |---------|----------|-----|-------|------------|----------|
   | Customer | restaurant | ✅ | ❌ | ❌ | ❌ |

#### 🔹 Inicio con Datos de Prueba

Si deseas cargar datos preexistentes:

```sh
python manage.py loaddata backup.json
```

> 📌 **Ubicación del archivo:** `backup.json` en la raíz del proyecto.

> *IMPORTANTE*
> Para efectos practicos de permitir iniciar con data inicial, se sube la carpeta media de lo contrario debes agregarla al `.gitignore` para que no se suban tus archivos
---

### 4️⃣ Descripción de Servicio con Mapeo de Puertos

> El mapeo de puertos se puede configurar en `docker-compose.yml`

| Servicio   | Descripción | URL |
|------------|------------|-----|
| **Django API Restful** | API principal del backend | `http://localhost:8000/` |
| **Base de datos PostgreSQL** | Almacenamiento de datos | `http://localhost:5432/` |
| **Redis** | Base de datos de caché y broker de mensajes | `http://localhost:6379/` |
| **Flower** | Visualización de tareas de Celery | `http://localhost:5555/` |

---

## 🔄 Migraciones de Modelos

Si se realizan cambios en `models.py`, ejecutar:

```sh
# Crear migraciones
python manage.py makemigrations
# Aplicar migraciones
python manage.py migrate
```

### 📤 Exportar Base de Datos

```sh
python manage.py dumpdata users restaurants orders --indent 2 > backup.json
```

### 📥 Importar Base de Datos

```sh
python manage.py loaddata backup.json
```

---

## ✅ Ejecutar Tests

Para ejecutar las pruebas, usa:

```sh
python manage.py test apps.restaurants
```

---

## ⏳ Tareas Asíncronas

El proyecto está integrado con **Celery**, permitiendo la ejecución de tareas asíncronas.

**Ejemplo:** Creación masiva de usuarios desde un archivo CSV:

```sh
python manage.py import_users
```

> 📌 **Ubicación del archivo CSV:** `/import/users.csv`

---

## 📖 Documentación de APIs

Puedes encontrar detalles de los endpoints en la carpeta `postman`.

📂 **Ubicación:** `postman/`

- **Colección de Postman:** `collection.json`
- **Entorno de Postman:** `environment.json`

Para importar en **Postman**:

1. Abre Postman.
2. Ve a `File > Import`.
3. Selecciona los archivos `collection.json` y `environment.json`.
4. Activa el environment y prueba los endpoints.

---

🎯 **Listo para usar!** 🚀
