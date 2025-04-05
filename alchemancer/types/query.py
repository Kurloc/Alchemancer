import sys
from abc import ABCMeta

# if python_version < 3.11
if sys.version_info[1] < 11:
    from typing_extensions import NotRequired, Self
else:
    from typing import NotRequired, Self

from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
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
    # this is for columns where we select and filter as a column select, very esoteric
    # most commonly used in subqueries
    select: NotRequired[Union[str, Dict[str, Self]]]
    where: NotRequired[WhereClausT]


class HqlJoin(TypedDict):
    select: Dict[str, HqlSelect]
    where: WhereClausT


class HqlCTE(TypedDict):
    name: str
    recursive: NotRequired[bool]


class HqlUnion(TypedDict):
    name: str
    left: "HqlQueryUnion"
    right: "HqlQueryUnion"
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
    distinct: NotRequired[Union[bool, List[str]]]
    subqueries: NotRequired[Dict[str, Self]]
    cte: NotRequired[HqlCTE]
    union: NotRequired[HqlUnion]
    union_all: NotRequired[HqlUnion]
    resolver_args: NotRequired[Dict[str, PrimitiveT]]
    debug: NotRequired[Literal["html", "str"]]


class HqlQueryUnion(HqlQuery):
    alias: NotRequired[str]


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
