from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.users.model import User, UserRole


class UserNotFoundError(Exception):
    pass


class UserValidationError(Exception):
    pass


class UserConflictError(Exception):
    pass


class UserService:

    @staticmethod
    def create(data: dict) -> User:
        """
        Crea un usuario nuevo.
        """

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        role_value = str(data.get("role", UserRole.EMPLOYEE.value)).upper()

        if not name:
            raise UserValidationError("El nombre es obligatorio")

        if not email:
            raise UserValidationError("El correo es obligatorio")

        if not password:
            raise UserValidationError("La contraseña es obligatoria")

        if len(password) < 8:
            raise UserValidationError(
                "La contraseña debe tener al menos 8 caracteres"
            )

        try:
            role = UserRole(role_value)
        except ValueError as error:
            raise UserValidationError(
                "El rol debe ser ADMIN o EMPLOYEE"
            ) from error

        existing_user = db.session.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            raise UserConflictError("El correo ya está registrado")

        user = User(
            name=name,
            email=email,
            role=role,
            is_active=True,
        )

        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

            return user

        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def get_all(
        include_inactive: bool = False,
        role: str | None = None,
    ) -> list[User]:
        """
        Obtiene todos los usuarios.

        Puede incluir usuarios inactivos y filtrar por rol.
        """

        statement = select(User)

        if not include_inactive:
            statement = statement.where(User.is_active.is_(True))

        if role:
            try:
                user_role = UserRole(role.upper())
            except ValueError as error:
                raise UserValidationError(
                    "El rol debe ser ADMIN o EMPLOYEE"
                ) from error

            statement = statement.where(User.role == user_role)

        statement = statement.order_by(User.created_at.desc())

        return list(db.session.scalars(statement).all())

    @staticmethod
    def get_by_id(user_id: int) -> User:
        """
        Obtiene un usuario por su identificador.
        """

        user = db.session.get(User, user_id)

        if not user:
            raise UserNotFoundError("Usuario no encontrado")

        return user

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """
        Busca un usuario por correo.
        Será útil para el inicio de sesión.
        """

        normalized_email = email.strip().lower()

        if not normalized_email:
            return None

        return db.session.scalar(
            select(User).where(User.email == normalized_email)
        )

    @staticmethod
    def update(user_id: int, data: dict) -> User:
        """
        Actualiza parcialmente un usuario.

        Solo modifica los campos enviados.
        """

        user = UserService.get_by_id(user_id)

        if "name" in data:
            name = str(data["name"]).strip()

            if not name:
                raise UserValidationError(
                    "El nombre no puede estar vacío"
                )

            user.name = name

        if "email" in data:
            email = str(data["email"]).strip().lower()

            if not email:
                raise UserValidationError(
                    "El correo no puede estar vacío"
                )

            existing_user = db.session.scalar(
                select(User).where(
                    User.email == email,
                    User.id != user_id,
                )
            )

            if existing_user:
                raise UserConflictError(
                    "El correo ya pertenece a otro usuario"
                )

            user.email = email

        if "role" in data:
            role_value = str(data["role"]).upper()

            try:
                user.role = UserRole(role_value)
            except ValueError as error:
                raise UserValidationError(
                    "El rol debe ser ADMIN o EMPLOYEE"
                ) from error

        if "password" in data:
            password = str(data["password"])

            if len(password) < 8:
                raise UserValidationError(
                    "La contraseña debe tener al menos 8 caracteres"
                )

            user.set_password(password)

        if "is_active" in data:
            is_active = data["is_active"]

            if not isinstance(is_active, bool):
                raise UserValidationError(
                    "is_active debe ser verdadero o falso"
                )

            user.is_active = is_active

        try:
            db.session.commit()
            db.session.refresh(user)

            return user

        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def delete(user_id: int) -> User:
        """
        Desactiva un usuario sin eliminarlo de la base de datos.
        """

        user = UserService.get_by_id(user_id)

        if not user.is_active:
            raise UserConflictError(
                "El usuario ya se encuentra desactivado"
            )

        user.is_active = False

        try:
            db.session.commit()
            db.session.refresh(user)

            return user

        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def restore(user_id: int) -> User:
        """
        Reactiva un usuario desactivado.
        """

        user = UserService.get_by_id(user_id)

        if user.is_active:
            raise UserConflictError(
                "El usuario ya se encuentra activo"
            )

        user.is_active = True

        try:
            db.session.commit()
            db.session.refresh(user)

            return user

        except SQLAlchemyError:
            db.session.rollback()
            raise