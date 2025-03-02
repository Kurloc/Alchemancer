from typing import Optional, List, Dict

from sqlalchemy import String, ForeignKey, JSON, Column
from sqlalchemy.orm import mapped_column, Mapped, relationship

from tests.fixtures.models.base_model import BaseModel


class Role(BaseModel):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_role_id: Mapped[int]
