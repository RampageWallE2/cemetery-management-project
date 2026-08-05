from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.users.model import UserRole
from app.users.service import UserNotFoundError, UserService


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        try:
            current_user_id = int(get_jwt_identity())
            current_user = UserService.get_by_id(current_user_id)

        except (TypeError, ValueError, UserNotFoundError):
            return jsonify({
                "error": "Usuario autenticado no válido"
            }), 401

        if not current_user.is_active:
            return jsonify({
                "error": "La cuenta está desactivada"
            }), 403

        if current_user.role != UserRole.ADMIN:
            return jsonify({
                "error": "Se requieren permisos de administrador"
            }), 403

        return function(*args, **kwargs)

    return wrapper