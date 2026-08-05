# Cementery Project

Sistema de gestión para cementerios orientado al control interno de empleados, fallecidos, familiares responsables, espacios disponibles y entierros.

El objetivo del proyecto es resolver un problema real de negocio: permitir que el personal de un cementerio gestione la disponibilidad de ubicaciones y asigne un espacio específico a una persona fallecida.

## Arquitectura

```text
Angular Frontend
        ↓
Go Reverse Proxy
        ↓
Flask REST API
        ↓
PostgreSQL
```

### Responsabilidades

* **Angular:** interfaz administrativa.
* **Go:** reverse proxy, validación y control de peticiones.
* **Flask:** autenticación, lógica de negocio y API REST.
* **PostgreSQL:** almacenamiento persistente.
* **Docker:** ejecución de la base de datos y servicios.

> Actualmente, el desarrollo está enfocado principalmente en el backend con Flask.

## Funcionalidades del MVP

El sistema estará dirigido inicialmente a trabajadores internos del cementerio.

### Administrador

* Iniciar sesión.
* Crear empleados.
* Consultar usuarios.
* Actualizar usuarios.
* Desactivar y reactivar empleados.
* Gestionar sectores y espacios.
* Consultar todos los registros.

### Empleado

* Iniciar sesión.
* Consultar su perfil.
* Registrar familiares responsables.
* Registrar personas fallecidas.
* Consultar espacios disponibles.
* Seleccionar y reservar una ubicación.
* Programar un entierro.
* Confirmar la ocupación de un espacio.

## Estado actual

### Implementado

* [x] Configuración inicial de Flask.
* [x] Application Factory Pattern.
* [x] Organización modular mediante Blueprints.
* [x] Integración con PostgreSQL.
* [x] PostgreSQL ejecutándose en Docker.
* [x] Configuración de Flask-SQLAlchemy.
* [x] Migraciones con Flask-Migrate.
* [x] Modelo de usuarios.
* [x] Roles `ADMIN` y `EMPLOYEE`.
* [x] Hash seguro de contraseñas.
* [x] CRUD de usuarios.
* [x] Desactivación lógica de usuarios.
* [x] Protección de rutas administrativas.
* [x] Inicio de sesión con JWT.
* [x] Consulta del usuario autenticado.

### Próximas funcionalidades

* [ ] Sectores del cementerio.
* [ ] Espacios de entierro.
* [ ] Estados de disponibilidad.
* [ ] Registro de familiares.
* [ ] Registro de fallecidos.
* [ ] Reservas.
* [ ] Entierros.
* [ ] Historial de cambios.
* [ ] Integración con Angular.
* [ ] Reverse proxy desarrollado en Go.
* [ ] Pruebas automatizadas.

## Tecnologías

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-JWT-Extended
* PostgreSQL
* Psycopg2
* Werkzeug

### Infraestructura

* Docker
* Docker Compose
* Git

### Tecnologías planificadas

* Angular
* Go

## Estructura del backend

```text
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   └── users/
│       ├── __init__.py
│       ├── model.py
│       ├── routes.py
│       └── service.py
│
├── migrations/
├── create_admin.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Patrón de organización

El backend utiliza:

* **Application Factory Pattern:** Flask se crea mediante `create_app()`.
* **Blueprints:** las rutas se organizan por módulos.
* **Service Layer:** la lógica de negocio se separa de las rutas.
* **Decorators:** los permisos se validan antes de ejecutar una ruta.
* **Repository modular:** cada dominio contiene sus modelos, servicios y rutas.

## Requisitos

Para ejecutar el backend necesitas:

* Python 3.13 o superior.
* PostgreSQL.
* Docker y Docker Compose.
* Git.

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd "Cementery Project/backend"
```

### 2. Crear un entorno virtual

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crea un archivo `.env` dentro de `backend/`.

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/cementery_db
JWT_SECRET_KEY=replace-with-a-secure-secret
JWT_ACCESS_TOKEN_MINUTES=60
```

También puedes definirlas temporalmente desde PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5432/cementery_db"
$env:JWT_SECRET_KEY="replace-with-a-secure-secret"
$env:JWT_ACCESS_TOKEN_MINUTES="60"
```

Las credenciales reales no deben subirse al repositorio.

## Base de datos con Docker

Levanta PostgreSQL:

```bash
docker compose up -d db
```

Comprueba que el contenedor esté activo:

```bash
docker compose ps
```

Para consultar las tablas:

```bash
docker exec -it cementeryproject-db-1 psql -U postgres -d cementery_db -c "\dt"
```

Para ver la estructura de la tabla `users`:

```bash
docker exec -it cementeryproject-db-1 psql -U postgres -d cementery_db -c "\d users"
```

## Migraciones

La carpeta `migrations/` debe mantenerse dentro del repositorio.

Inicializa las migraciones únicamente la primera vez:

```bash
python -m flask --app "app:create_app" db init
```

Genera una migración:

```bash
python -m flask --app "app:create_app" db migrate -m "create users table"
```

Aplica los cambios:

```bash
python -m flask --app "app:create_app" db upgrade
```

Comprueba la versión actual:

```bash
python -m flask --app "app:create_app" db current
```

Cada vez que cambien los modelos:

```bash
python -m flask --app "app:create_app" db migrate -m "description"
python -m flask --app "app:create_app" db upgrade
```

## Crear el primer administrador

Las rutas de usuarios están protegidas para administradores. Por eso es necesario crear inicialmente un usuario administrador mediante el script:

```bash
python create_admin.py
```

Después de crear el administrador, el script puede eliminarse o reemplazarse posteriormente por un comando personalizado de Flask.

## Ejecutar el backend

```bash
python -m flask --app "app:create_app" run --debug
```

La API estará disponible en:

```text
http://localhost:5000
```

## Autenticación

El sistema utiliza tokens JWT.

### Iniciar sesión

```http
POST /api/auth/login
Content-Type: application/json
```

```json
{
  "email": "admin@cementerio.com",
  "password": "Admin12345"
}
```

Respuesta esperada:

```json
{
  "message": "Inicio de sesión correcto",
  "access_token": "JWT_TOKEN",
  "user": {
    "id": 1,
    "name": "Administrador",
    "email": "admin@cementerio.com",
    "role": "ADMIN",
    "is_active": true
  }
}
```

### Enviar el token

Las rutas protegidas deben recibir:

```http
Authorization: Bearer JWT_TOKEN
```

### Consultar la sesión actual

```http
GET /api/auth/me
Authorization: Bearer JWT_TOKEN
```

## Endpoints actuales

### Autenticación

| Método | Endpoint          | Acceso      | Descripción            |
| ------ | ----------------- | ----------- | ---------------------- |
| `POST` | `/api/auth/login` | Público     | Iniciar sesión         |
| `GET`  | `/api/auth/me`    | Autenticado | Obtener usuario actual |

### Usuarios

| Método   | Endpoint                  | Acceso        | Descripción        |
| -------- | ------------------------- | ------------- | ------------------ |
| `POST`   | `/api/users`              | Administrador | Crear usuario      |
| `GET`    | `/api/users`              | Administrador | Listar usuarios    |
| `GET`    | `/api/users/<id>`         | Administrador | Consultar usuario  |
| `PATCH`  | `/api/users/<id>`         | Administrador | Actualizar usuario |
| `DELETE` | `/api/users/<id>`         | Administrador | Desactivar usuario |
| `PATCH`  | `/api/users/<id>/restore` | Administrador | Reactivar usuario  |

## Roles

### `ADMIN`

Puede gestionar usuarios y acceder a las operaciones administrativas.

### `EMPLOYEE`

Puede iniciar sesión y utilizar las funcionalidades operativas que se implementarán para familiares, fallecidos, ubicaciones y entierros.

Un empleado no puede:

* Crear administradores.
* Crear otros empleados.
* Cambiar roles.
* Desactivar cuentas.
* Consultar el CRUD administrativo de usuarios.

## Flujo principal planificado

```text
Empleado inicia sesión
        ↓
Registra al familiar responsable
        ↓
Registra a la persona fallecida
        ↓
Consulta los espacios disponibles
        ↓
Selecciona una ubicación
        ↓
Reserva el espacio
        ↓
Programa el entierro
        ↓
Confirma la ocupación
```

## Modelo inicial de ubicaciones

```text
Cementerio
└── Sector
    └── Espacio de entierro
```

Ejemplo:

```text
Sector A
Espacio A-001
Estado: AVAILABLE
```

Estados planificados:

```text
AVAILABLE
RESERVED
OCCUPIED
BLOCKED
MAINTENANCE
```

## Reglas principales del negocio

* Un espacio ocupado no puede reservarse nuevamente.
* Un espacio reservado no puede asignarse a dos entierros activos.
* Un fallecido solo puede tener una ubicación activa.
* Un usuario desactivado no puede iniciar sesión.
* Solo un administrador puede gestionar empleados.
* Las contraseñas nunca se almacenan en texto plano.
* Las eliminaciones de usuarios son lógicas para conservar el historial.

## Seguridad

* Contraseñas almacenadas mediante hash.
* Rutas protegidas con JWT.
* Validación del estado del usuario en cada operación administrativa.
* Control de acceso basado en roles.
* Variables sensibles excluidas del repositorio.
* Mensajes genéricos cuando las credenciales son incorrectas.

## Autor

**Piero Valentino Noa Chahuayo**

Proyecto desarrollado como parte de un portafolio profesional de desarrollo de software.
