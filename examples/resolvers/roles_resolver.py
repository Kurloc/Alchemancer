from typing import Any, Dict, List

from sqlalchemy import Column, Integer, Select, String, or_, select

from alchemancer.types.resolver import HqlResolver, HqlResolverParameter
from tests.fixtures.models.role import Role


class RecursiveRolesResolver(HqlResolver):
    @property
    def parameters(self) -> Dict[str, HqlResolverParameter]:
        return {
            "role_id": HqlResolverParameter(int),
        }

    @property
    def columns(self) -> List[Column]:
        return [
            Column("role_id", Integer),
            Column("role_name", String),
            Column("role_parent_id", Integer, nullable=True),
        ]

    def _insert_data_hook(self, **kwargs) -> List[Dict[str, Any]]:
        # you can do literally anything here to produce the records
        return [
            {"role_id": 1, "role_name": 1, "role_parent_id": None},
            {"role_id": 2, "role_name": 2, "role_parent_id": 1},
            {"role_id": 3, "role_name": 3, "role_parent_id": 1},
            {"role_id": 4, "role_name": 4, "role_parent_id": 1},
            {"role_id": 5, "role_name": 5, "role_parent_id": None},
            {"role_id": 6, "role_name": 6, "role_parent_id": 5},
            {"role_id": 7, "role_name": 7, "role_parent_id": 5},
            {"role_id": 8, "role_name": 8, "role_parent_id": 5},
        ]

    def _execute_hook(self, **kwargs) -> Select:
        role_id = kwargs.get("role_id")

        cte = select(
            self.table.c.role_id,
            self.table.c.role_name,
            self.table.c.role_parent_id,
        )
        union_cte = cte.union_all(
            select(
                cte.c.role_id.label("role_id"),
                cte.c.role_name.label("role_name"),
                Role.id.label("role_parent_id"),
            )
            .join(Role, Role.id == cte.c.role_parent_id)
            .filter(
                or_(
                    cte.c.role_id == role_id,
                    cte.c.role_parent_id == role_id,
                )
            )
        ).cte(recursive=True, name="roles_base_cte")

        return select(union_cte.columns)
