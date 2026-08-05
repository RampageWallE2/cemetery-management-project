from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.users.service import (
    UserConflictError,
    UserService,
    UserValidationError,
)


app = create_app()


with app.app_context():
    try:
        admin = UserService.create({
            "name": "Administrador",
            "email": "admin@cementerio.com",
            "password": "Admin12345",
            "role": "ADMIN",
        })

        print("Administrador creado:")
        print(admin.to_dict())

    except UserConflictError as error:
        print(f"No se creó: {error}")

    except UserValidationError as error:
        print(f"Datos inválidos: {error}")

    except SQLAlchemyError as error:
        print(f"Error de base de datos: {error}")