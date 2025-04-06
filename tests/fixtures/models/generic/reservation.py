from datetime import datetime

import sqlalchemy
from sqlalchemy import (
    ForeignKey,
    Integer,
    TextClause,
)
from sqlalchemy.orm import Mapped, mapped_column

from tests.fixtures.models.generic.base_model import BaseModel


class Reservation(BaseModel):
    __tablename__ = "reservation"
    id: Mapped[int] = mapped_column(primary_key=True)
    """When the reservation is scheduled to start."""
    date_time_start: Mapped[datetime]
    """When the reservation is scheduled to end or the customer will be charged additional fees."""
    date_time_end: Mapped[datetime]
    """The number of miles the reservation is allotted, if it -1, then the mileage is unlimited"""
    allotted_miles: Mapped[int] = mapped_column(server_default=TextClause("-1"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    customer_pick_up_time: Mapped[datetime] = mapped_column(nullable=True)
    customer_return_time: Mapped[datetime] = mapped_column(nullable=True)
    insurance_plan: Mapped[bool] = mapped_column(
        server_default=sqlalchemy.sql.expression.false()
    )

    user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))


class ReservationDriverAssociation(BaseModel):
    """
    We use a driver reservation junction table so multiple drivers can be associated with a reservation.
    """

    __tablename__ = "reservation_driver_association"
    reservation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservation.id"),
        primary_key=True,
    )
    driver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("driver.id"),
        primary_key=True,
    )
