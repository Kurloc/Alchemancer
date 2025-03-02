import abc
from abc import ABCMeta
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    NotRequired,
    Optional,
    Self,
    Type,
    TypedDict,
    Union,
)

from sqlalchemy import (
    Column,
    ColumnElement,
    Connection,
    CursorResult,
    Executable,
    Select,
)
from sqlalchemy.engine.interfaces import (
    CoreExecuteOptionsParameter,
    _CoreAnyExecuteParams,
)
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.reflection_handler import ReflectionHandler
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


# Resolver Models
class ResolverParameter:
    default_value: Union[Any, Callable]
    optional: bool = False
    python_type: Type[Any]


class HqlResolver(metaclass=ABCMeta):
    __reflection_handler: ReflectionHandler
    __table: str
    __connection: Connection
    __execution_query: HqlQuery
    __executed: bool

    @property
    @abc.abstractmethod
    def resolver_parameters(self) -> Dict[str, ResolverParameter]:
        return {}

    def __init__(
        self,
        connection: Optional[Connection] = None,
        reflection_handler: Optional[ReflectionHandler] = None,
        **kwargs,
    ):
        self.__connection = connection
        self.__reflection_handler = reflection_handler


class TRe(HqlResolver):
    resolver_parameters = {"test": object()}
