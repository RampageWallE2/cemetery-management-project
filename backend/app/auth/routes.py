from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from app.auth.service import (
    AuthService,
    AuthValidationError,
    DisabledAccountError,
    InvalidCredentialsError,
)
from app.users.service import (
    UserNotFoundError,
    UserService,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """
    Inicia sesión.

    POST /api/auth/login
    """

    try:
        data = request.get_json(silent=True)

        user, access_token = AuthService.login(data)

        return jsonify({
            "message": "Inicio de sesión correcto",
            "access_token": access_token,
            "user": user.to_dict(),
        }), 200

    except AuthValidationError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except InvalidCredentialsError as error:
        return jsonify({
            "error": str(error)
        }), 401

    except DisabledAccountError as error:
        return jsonify({
            "error": str(error)
        }), 403

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo completar el inicio de sesión"
        }), 500


@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    """
    Obtiene el usuario autenticado.

    GET /api/auth/me
    """

    try:
        current_user_id = int(get_jwt_identity())
        user = UserService.get_by_id(current_user_id)

        if not user.is_active:
            return jsonify({
                "error": "La cuenta está desactivada"
            }), 403

        return jsonify({
            "user": user.to_dict()
        }), 200

    except (TypeError, ValueError, UserNotFoundError):
        return jsonify({
            "error": "Usuario autenticado no válido"
        }), 401

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo obtener el usuario autenticado"
        }), 500