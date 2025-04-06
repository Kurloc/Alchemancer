from datetime import datetime

from sqlalchemy import VARCHAR, Column, Computed, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from tests.fixtures.models.generic.base_model import BaseModel


class Vin(BaseModel):
    """
    Using ISO 3780
    """

    __tablename__ = "vin"
    id: Mapped[int] = mapped_column(primary_key=True)
    wmi: Mapped[str] = mapped_column(VARCHAR(3), nullable=False)
    vds: Mapped[str] = mapped_column(VARCHAR(6), nullable=False)
    vis: Mapped[str] = mapped_column(VARCHAR(8), nullable=False)
    vin = Column(
        VARCHAR,
        Computed("wmi || vds || vis"),
        unique=True,
    )


# @TODO: need to finish this model, going to try and make a simple set of DB models for a very basic version of
#  something like uhaul or a car rental service.
class Vehicle(BaseModel):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_entry_created: Mapped[datetime] = mapped_column(server_default=func.now())
    vin = mapped_column(VARCHAR(17), ForeignKey("vin.vin"), unique=True)
