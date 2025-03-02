from abc import ABCMeta
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NotRequired,
    Optional,
    Self,
    TypedDict,
    Union,
)

from sqlalchemy import Column, Connection, CursorResult, Executable, Select
from sqlalchemy.engine.interfaces import (
    CoreExecuteOptionsParameter,
    _CoreAnyExecuteParams,
)
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.sql.elements import ColumnElement, KeyedColumnElement

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
        str,
        # let's see if this can be slimmed down from ANY to a recursive typing maybe?
        any,
    ],
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
PrimitiveT = Union[
    int,
    str,
    float,
    bool,
    List[str],
    List[int],
    List[float],
    List[bool],
    Dict[str, str],
    Dict[str, int],
    Dict[str, float],
    Dict[str, bool],
    Dict[bool, bool],
    Dict[bool, str],
    Dict[bool, int],
    Dict[bool, float],
    Dict[int, bool],
    Dict[int, str],
    Dict[int, int],
    Dict[int, float],
    Dict[float, bool],
    Dict[float, str],
    Dict[float, int],
    Dict[float, float],
]

WhereClausT = Dict[str, ValueTypesT]


# QUERY models
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


class HqlJoin(TypedDict):
    select: Dict[str, HqlSelect]
    where: WhereClausT


class HqlCTE(TypedDict):
    name: str
    recursive: NotRequired[bool]


class HqlUnion(TypedDict):
    name: str
    left: "HqlQuery"
    right: "HqlQuery"
    cte: HqlCTE


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
    cte: NotRequired[HqlCTE]
    union: NotRequired[HqlUnion]
    union_all: NotRequired[HqlUnion]
    alias: NotRequired[str]
    debug: NotRequired[Literal["html", "str"]]


# Generator Models
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


class JsonPlugin(metaclass=ABCMeta):
    sqlalchemy_functions: Dict[str, Any]
