from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from app.auth.decorators import admin_required
from app.locations.service import (
    SectorService,
    BurialSpaceService,
    LocationNotFoundError,
    LocationValidationError,
    LocationConflictError,
)


locations_bp = Blueprint("locations", __name__, url_prefix="/api/location")


# =========================================================
# SECTORS
# =========================================================

@locations_bp.post("/sectors")
@admin_required
def create_sector():
    data = request.get_json(silent=True)

    try:
        sector = SectorService.create(data)

        return jsonify({
            "message": "Sector creado correctamente",
            "sector": sector.to_dict()
        }), 201

    except LocationValidationError as error:
        return jsonify({"error": str(error)}), 400

    except LocationConflictError as error:
        return jsonify({"error": str(error)}), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.get("/sectors")
@jwt_required()
def get_sectors():
    include_inactive = (
        request.args.get("include_inactive", "false").lower()
        == "true"
    )

    try:
        sectors = SectorService.get_all(
            include_inactive=include_inactive
        )

        return jsonify({
            "sectors": [
                sector.to_dict()
                for sector in sectors
            ]
        }), 200

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.get("/sectors/<int:sector_id>")
@jwt_required()
def get_sector(sector_id):
    try:
        sector = SectorService.get_by_id(sector_id)

        return jsonify({
            "sector": sector.to_dict()
        }), 200

    except LocationNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.patch("/sectors/<int:sector_id>")
@admin_required
def update_sector(sector_id):
    data = request.get_json(silent=True)

    try:
        sector = SectorService.update(
            sector_id,
            data
        )

        return jsonify({
            "message": "Sector actualizado correctamente",
            "sector": sector.to_dict()
        }), 200

    except LocationValidationError as error:
        return jsonify({"error": str(error)}), 400

    except LocationNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except LocationConflictError as error:
        return jsonify({"error": str(error)}), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


# =========================================================
# BURIAL SPACES
# =========================================================

@locations_bp.post("/spaces")
@admin_required
def create_burial_space():
    data = request.get_json(silent=True)

    try:
        space = BurialSpaceService.create(data)

        return jsonify({
            "message": "Ubicación creada correctamente",
            "burial_space": space.to_dict()
        }), 201

    except LocationValidationError as error:
        return jsonify({"error": str(error)}), 400

    except LocationNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except LocationConflictError as error:
        return jsonify({"error": str(error)}), 409

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.get("/spaces")
@jwt_required()
def get_burial_spaces():
    sector_id = request.args.get(
        "sector_id",
        type=int
    )

    block_letter = request.args.get(
        "block_letter"
    )

    row_number = request.args.get(
        "row_number",
        type=int
    )

    status = request.args.get(
        "status"
    )

    try:
        spaces = BurialSpaceService.get_all(
            sector_id=sector_id,
            block_letter=block_letter,
            row_number=row_number,
            status=status
        )

        return jsonify({
            "burial_spaces": [
                space.to_dict()
                for space in spaces
            ]
        }), 200

    except LocationValidationError as error:
        return jsonify({"error": str(error)}), 400

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.get("/spaces/<int:space_id>")
@jwt_required()
def get_burial_space(space_id):
    try:
        space = BurialSpaceService.get_by_id(
            space_id
        )

        return jsonify({
            "burial_space": space.to_dict()
        }), 200

    except LocationNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500


@locations_bp.patch("/spaces/<int:space_id>/status")
@admin_required
def update_burial_space_status(space_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")

    try:
        space = BurialSpaceService.update_status(
            space_id,
            status
        )

        return jsonify({
            "message": "Estado actualizado correctamente",
            "burial_space": space.to_dict()
        }), 200

    except LocationValidationError as error:
        return jsonify({"error": str(error)}), 400

    except LocationNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except SQLAlchemyError:
        return jsonify({
            "error": "Error interno de base de datos"
        }), 500