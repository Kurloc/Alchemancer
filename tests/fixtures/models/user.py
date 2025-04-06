from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tests.fixtures.models.base_model import BaseModel


class Address(BaseModel):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="addresses")


class User(BaseModel):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    date_create: Mapped[datetime] = mapped_column(server_default=func.now())
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    account_balance: Mapped[float] = mapped_column(default=0.0)
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    account_details = mapped_column(
        JSON, default={"test": "123", "nested": {"inner_test": 234}}
    )


class Driver(BaseModel):
    __tablename__ = "driver"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    drivers_license_id: Mapped[str] = mapped_column(unique=True)


#
# spongebob = User(
#          name="spongebob",
#          fullname="Spongebob Squarepants",
#          addresses=[Address(email_address="spongebob@sqlalchemy.org")],
#      )
# print(spongebob)
