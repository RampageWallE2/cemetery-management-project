# app/locations/model.py

from datetime import datetime, timezone
from enum import Enum

from app.extensions import db


class BurialSpaceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    BLOCKED = "BLOCKED"
    MAINTENANCE = "MAINTENANCE"


class Sector(db.Model):
    __tablename__ = "sectors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    burial_spaces = db.relationship(
        "BurialSpace",
        back_populates="sector"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BurialSpace(db.Model):
    __tablename__ = "burial_spaces"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sector_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "sectors.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    block_letter = db.Column(
        db.String(1),
        nullable=False
    )

    row_number = db.Column(
        db.Integer,
        nullable=False
    )

    location_number = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.Enum(
            BurialSpaceStatus,
            name="burial_space_status",
            native_enum=True
        ),
        nullable=False,
        default=BurialSpaceStatus.AVAILABLE
    )

    notes = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    sector = db.relationship(
        "Sector",
        back_populates="burial_spaces"
    )

    __table_args__ = (
        db.CheckConstraint(
            "row_number BETWEEN 1 AND 20",
            name="ck_burial_space_row_number"
        ),
        db.CheckConstraint(
            "location_number BETWEEN 1 AND 20",
            name="ck_burial_space_location_number"
        ),
        db.UniqueConstraint(
            "sector_id",
            "block_letter",
            "row_number",
            "location_number",
            name="uq_burial_space_location"
        ),
    )

    @property
    def row_type(self):
        return "EVEN" if self.row_number % 2 == 0 else "ODD"

    @property
    def code(self):
        return (
            f"{self.sector.code}-"
            f"{self.block_letter}-"
            f"{self.row_number:02d}-"
            f"{self.location_number:02d}"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "sector_id": self.sector_id,
            "sector_code": self.sector.code,
            "block_letter": self.block_letter,
            "row_number": self.row_number,
            "row_type": self.row_type,
            "location_number": self.location_number,
            "code": self.code,
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }