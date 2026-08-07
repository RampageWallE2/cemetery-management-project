from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.locations.model import Sector, BurialSpace, BurialSpaceStatus


class LocationNotFoundError(Exception):
    pass


class LocationValidationError(Exception):
    pass


class LocationConflictError(Exception):
    pass


class SectorService:

    @staticmethod
    def create(data):
        if not isinstance(data, dict):
            raise LocationValidationError("Datos inválidos")

        code = str(data.get("code", "")).strip().upper()
        name = str(data.get("name", "")).strip()
        description = data.get("description")

        if not code:
            raise LocationValidationError("El código del sector es obligatorio")

        if not name:
            raise LocationValidationError("El nombre del sector es obligatorio")

        existing_sector = db.session.scalar(
            select(Sector).where(Sector.code == code)
        )

        if existing_sector:
            raise LocationConflictError(
                "Ya existe un sector con ese código"
            )

        sector = Sector(
            code=code,
            name=name,
            description=description
        )

        try:
            db.session.add(sector)
            db.session.commit()
            db.session.refresh(sector)

            return sector

        except SQLAlchemyError:
            db.session.rollback()
            raise


    @staticmethod
    def get_all(include_inactive=False):
        query = select(Sector)

        if not include_inactive:
            query = query.where(Sector.is_active.is_(True))

        query = query.order_by(Sector.code)

        return db.session.scalars(query).all()


    @staticmethod
    def get_by_id(sector_id):
        sector = db.session.get(Sector, sector_id)

        if not sector:
            raise LocationNotFoundError("Sector no encontrado")

        return sector


    @staticmethod
    def update(sector_id, data):
        sector = SectorService.get_by_id(sector_id)

        if "code" in data:
            code = str(data["code"]).strip().upper()

            if not code:
                raise LocationValidationError(
                    "El código del sector no puede estar vacío"
                )

            existing = db.session.scalar(
                select(Sector).where(
                    Sector.code == code,
                    Sector.id != sector_id
                )
            )

            if existing:
                raise LocationConflictError(
                    "Ya existe otro sector con ese código"
                )

            sector.code = code

        if "name" in data:
            name = str(data["name"]).strip()

            if not name:
                raise LocationValidationError(
                    "El nombre no puede estar vacío"
                )

            sector.name = name

        if "description" in data:
            sector.description = data["description"]

        if "is_active" in data:
            sector.is_active = bool(data["is_active"])

        try:
            db.session.commit()
            db.session.refresh(sector)

            return sector

        except SQLAlchemyError:
            db.session.rollback()
            raise

class BurialSpaceService:

    @staticmethod
    def create(data):
        if not isinstance(data, dict):
            raise LocationValidationError("Datos inválidos")

        sector_id = data.get("sector_id")
        block_letter = str(
            data.get("block_letter", "")
        ).strip().upper()

        row_number = data.get("row_number")
        location_number = data.get("location_number")
        notes = data.get("notes")

        # Verificar sector
        sector = SectorService.get_by_id(sector_id)

        if not sector.is_active:
            raise LocationValidationError(
                "No se pueden crear espacios en un sector inactivo"
            )

        # Validar letra
        if (
            len(block_letter) != 1
            or not block_letter.isalpha()
        ):
            raise LocationValidationError(
                "La letra debe ser una única letra válida"
            )

        # Validar número par/impar
        try:
            row_number = int(row_number)
        except (TypeError, ValueError):
            raise LocationValidationError(
                "El número debe ser un entero"
            )

        if not 1 <= row_number <= 20:
            raise LocationValidationError(
                "El número debe estar entre 1 y 20"
            )

        # Validar ubicación
        try:
            location_number = int(location_number)
        except (TypeError, ValueError):
            raise LocationValidationError(
                "El número de ubicación debe ser un entero"
            )

        if not 1 <= location_number <= 20:
            raise LocationValidationError(
                "La ubicación debe estar entre 1 y 20"
            )

        # Evitar duplicados
        existing_space = db.session.scalar(
            select(BurialSpace).where(
                BurialSpace.sector_id == sector_id,
                BurialSpace.block_letter == block_letter,
                BurialSpace.row_number == row_number,
                BurialSpace.location_number == location_number
            )
        )

        if existing_space:
            raise LocationConflictError(
                "Esa ubicación ya existe"
            )

        burial_space = BurialSpace(
            sector_id=sector_id,
            block_letter=block_letter,
            row_number=row_number,
            location_number=location_number,
            status=BurialSpaceStatus.AVAILABLE,
            notes=notes
        )

        try:
            db.session.add(burial_space)
            db.session.commit()
            db.session.refresh(burial_space)

            return burial_space

        except SQLAlchemyError:
            db.session.rollback()
            raise


    @staticmethod
    def get_by_id(space_id):
        space = db.session.get(BurialSpace, space_id)

        if not space:
            raise LocationNotFoundError(
                "Espacio no encontrado"
            )

        return space


    @staticmethod
    def get_all(
        sector_id=None,
        block_letter=None,
        row_number=None,
        status=None
    ):
        query = select(BurialSpace)

        if sector_id is not None:
            query = query.where(
                BurialSpace.sector_id == sector_id
            )

        if block_letter:
            query = query.where(
                BurialSpace.block_letter
                == block_letter.strip().upper()
            )

        if row_number is not None:
            query = query.where(
                BurialSpace.row_number == row_number
            )

        if status:
            try:
                parsed_status = BurialSpaceStatus(
                    status.upper()
                )
            except ValueError:
                raise LocationValidationError(
                    "Estado de ubicación inválido"
                )

            query = query.where(
                BurialSpace.status == parsed_status
            )

        query = query.order_by(
            BurialSpace.sector_id,
            BurialSpace.block_letter,
            BurialSpace.row_number,
            BurialSpace.location_number
        )

        return db.session.scalars(query).all()


    @staticmethod
    def update_status(space_id, status):
        space = BurialSpaceService.get_by_id(space_id)

        try:
            new_status = BurialSpaceStatus(
                str(status).upper()
            )
        except ValueError:
            raise LocationValidationError(
                "Estado de ubicación inválido"
            )

        space.status = new_status

        try:
            db.session.commit()
            db.session.refresh(space)

            return space

        except SQLAlchemyError:
            db.session.rollback()
            raise