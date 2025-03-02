from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from tests.fixtures.models.base_model import BaseModel


class Reservation(BaseModel):
    __tablename__ = "reservation"
    id: Mapped[int] = mapped_column(primary_key=True)
    date_time_start: Mapped[datetime]
    date_time_end: Mapped[datetime]
    resource_id: Mapped[int]
