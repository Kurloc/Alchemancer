from typing import TypedDict, Literal, NotRequired, List, Union, Dict, Any, Optional, Self

from sqlalchemy import (
    Column,
    ColumnElement,
    Select,
    Executable,
    Connection,
    CursorResult,
)
from sqlalchemy.engine.interfaces import (
    CoreExecuteOptionsParameter,
    _CoreAnyExecuteParams,
)
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.sql.elements import KeyedColumnElement

ColumnTypesT = Union[
    Column,
    ColumnElement,
    InstrumentedAttribute,
    KeyedColumnElement,
    RelationshipProperty,
]

ColumnListT = List[ColumnTypesT]
ValueTypesT = Union[
    Dict[
        str, any
    ],  # let's see if this can be slimmed down from ANY to a recursive typing maybe?
    int,
    str,
    float,
    bool,
    List[int],
    List[str],
    List[float],
    List[bool],
    "HqlSelect",
]

WhereClausT = Dict[str, ValueTypesT]


class HqlSort(TypedDict):
    dir: Literal["asc", "desc"]
    index: int
    nulls_last: NotRequired[bool]


class HqlWhenThen(TypedDict):
    when: WhereClausT
    then: Union[str, "HqlSelect"]


class HqlSelect(TypedDict):
    label: NotRequired[str]
    distinct: NotRequired[bool]
    value: NotRequired[ValueTypesT]
    whens: NotRequired[List[HqlWhenThen]]
    else_: NotRequired["HqlSelect"]
    # select: NotRequired[Union[str, Dict[str, "HqlSelect"]]]
    # where: NotRequired[WhereClausT]


class HqlJoin(TypedDict):
    select: Dict[str, HqlSelect]
    where: WhereClausT


class HqlQuery(TypedDict):
    select: Dict[str, Dict[str, HqlSelect]]
    joins: NotRequired[Dict[str, HqlJoin]]
    where: NotRequired[WhereClausT]
    having: NotRequired[WhereClausT]
    limit: NotRequired[int]
    offset: NotRequired[int]
    order_by: NotRequired[Dict[str, HqlSort]]
    group_by: NotRequired[List[str]]
    distinct: NotRequired[bool]
    subqueries: NotRequired[Dict[str, Self]]
    debug: NotRequired[Literal["html", "str"]]


class GeneratedQuery:
    query: Select
    limit: Optional[int]
    offset: Optional[int]

    def __init__(
        self, query: Select, limit: Optional[int] = None, offset: Optional[int] = None
    ):
        self.query = query
        self.limit = limit
        self.offset = offset


class NoOpConnection(Connection):
    def execute(
        self,
        statement: Executable,
        parameters: Optional[_CoreAnyExecuteParams] = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> CursorResult[Any]:
        pass
