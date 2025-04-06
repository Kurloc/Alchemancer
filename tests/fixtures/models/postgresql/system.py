"""
This file exists for testing the integration of Alchemancer with the DB engine specific types. Like in postgresql
there are networking types that are useful and should be usable.
"""

from datetime import datetime

from sqlalchemy import TypeDecorator, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from tests.fixtures.models.postgresql.psql_base_model import PsqlBaseModel


class IPNetwork(TypeDecorator):
    impl = postgresql.INET
    python_type = str

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        return str(value)


class CIDR(TypeDecorator):
    impl = postgresql.CIDR
    python_type = str

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        return str(value)


class MacAddress(TypeDecorator):
    impl = postgresql.MACADDR
    python_type = str

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        return str(value)


class MacAddress8(TypeDecorator):
    impl = postgresql.MACADDR8
    python_type = str

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)

    def process_result_value(self, value, dialect):
        return str(value)


class System(PsqlBaseModel):
    __tablename__ = "system"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_create: Mapped[datetime] = mapped_column(server_default=func.now())
    """7 or 19 bytes IPv4 and IPv6 networks"""
    cidr: Mapped[str] = mapped_column(CIDR)
    """7 or 19 bytes IPv4 and IPv6 hosts and networks"""
    inet: Mapped[str] = mapped_column(IPNetwork)
    """6 bytes MAC addresses"""
    macaddr: Mapped[str] = mapped_column(MacAddress)
    """	8 bytes	MAC addresses (EUI-64 format)"""
    macaddr8: Mapped[str] = mapped_column(MacAddress8)
