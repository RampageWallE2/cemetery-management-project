from flask_jwt_extended import create_access_token

from app.users.service import UserService


class AuthValidationError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class DisabledAccountError(Exception):
    pass


class AuthService:

    @staticmethod
    def login(data: dict):
        """
        Valida las credenciales y genera un token JWT.
        """

        if not isinstance(data, dict):
            raise AuthValidationError(
                "El cuerpo de la petición debe ser un objeto JSON"
            )

        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not email:
            raise AuthValidationError(
                "El correo es obligatorio"
            )

        if not password:
            raise AuthValidationError(
                "La contraseña es obligatoria"
            )

        user = UserService.get_by_email(email)

        # Usamos el mismo mensaje para correo o contraseña incorrectos.
        if user is None or not user.check_password(password):
            raise InvalidCredentialsError(
                "Correo o contraseña incorrectos"
            )

        if not user.is_active:
            raise DisabledAccountError(
                "La cuenta está desactivada"
            )

        access_token = create_access_token(
            identity=str(user.id)
        )

        return user, access_token