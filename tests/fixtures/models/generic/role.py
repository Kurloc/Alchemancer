from sqlalchemy.orm import Mapped, mapped_column

from tests.fixtures.models.generic.base_model import BaseModel


class Role(BaseModel):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_role_id: Mapped[int]
