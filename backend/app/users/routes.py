from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.auth.decorators import admin_required
from app.users.service import (
    UserConflictError,
    UserNotFoundError,
    UserService,
    UserValidationError,
)


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.post("/")
@admin_required
def create_user():
    """
    Crea un administrador o empleado.

    POST /api/users
    """

    try:
        data = request.get_json(silent=True) or {}

        user = UserService.create(data)

        return jsonify({
            "message": "Usuario creado correctamente",
            "user": user.to_dict(),
        }), 201

    except UserValidationError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except UserConflictError as error:
        return jsonify({
            "error": str(error)
        }), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo crear el usuario"
        }), 500


@users_bp.get("/")
@admin_required
def get_users():
    """
    Lista los usuarios.

    GET /api/users
    GET /api/users?include_inactive=true
    GET /api/users?role=EMPLOYEE
    """

    try:
        include_inactive_value = request.args.get(
            "include_inactive",
            "false"
        ).strip().lower()

        if include_inactive_value not in {"true", "false"}:
            raise UserValidationError(
                "include_inactive debe ser true o false"
            )

        include_inactive = include_inactive_value == "true"
        role = request.args.get("role")

        users = UserService.get_all(
            include_inactive=include_inactive,
            role=role,
        )

        return jsonify({
            "users": [
                user.to_dict()
                for user in users
            ],
            "total": len(users),
        }), 200

    except UserValidationError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudieron obtener los usuarios"
        }), 500


@users_bp.get("/<int:user_id>")
@admin_required
def get_user(user_id: int):
    """
    Obtiene un usuario por ID.

    GET /api/users/1
    """

    try:
        user = UserService.get_by_id(user_id)

        return jsonify({
            "user": user.to_dict()
        }), 200

    except UserNotFoundError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo obtener el usuario"
        }), 500


@users_bp.patch("/<int:user_id>")
@admin_required
def update_user(user_id: int):
    """
    Actualiza parcialmente un usuario.

    PATCH /api/users/1
    """

    try:
        data = request.get_json(silent=True) or {}

        if not data:
            raise UserValidationError(
                "Debes enviar al menos un campo para actualizar"
            )

        current_user_id = int(get_jwt_identity())

        if user_id == current_user_id:
            new_role = str(data.get("role", "")).upper()

            if new_role and new_role != "ADMIN":
                raise UserConflictError(
                    "No puedes quitarte tu propio rol de administrador"
                )

            if data.get("is_active") is False:
                raise UserConflictError(
                    "No puedes desactivar tu propia cuenta"
                )

        user = UserService.update(user_id, data)

        return jsonify({
            "message": "Usuario actualizado correctamente",
            "user": user.to_dict(),
        }), 200

    except UserValidationError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except UserNotFoundError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except UserConflictError as error:
        return jsonify({
            "error": str(error)
        }), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo actualizar el usuario"
        }), 500


@users_bp.delete("/<int:user_id>")
@admin_required
def delete_user(user_id: int):
    """
    Desactiva un usuario.

    DELETE /api/users/1
    """

    try:
        current_user_id = int(get_jwt_identity())

        if user_id == current_user_id:
            raise UserConflictError(
                "No puedes desactivar tu propia cuenta"
            )

        user = UserService.delete(user_id)

        return jsonify({
            "message": "Usuario desactivado correctamente",
            "user": user.to_dict(),
        }), 200

    except UserNotFoundError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except UserConflictError as error:
        return jsonify({
            "error": str(error)
        }), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo desactivar el usuario"
        }), 500


@users_bp.patch("/<int:user_id>/restore")
@admin_required
def restore_user(user_id: int):
    """
    Reactiva un usuario desactivado.

    PATCH /api/users/1/restore
    """

    try:
        user = UserService.restore(user_id)

        return jsonify({
            "message": "Usuario reactivado correctamente",
            "user": user.to_dict(),
        }), 200

    except UserNotFoundError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except UserConflictError as error:
        return jsonify({
            "error": str(error)
        }), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "No se pudo reactivar el usuario"
        }), 500