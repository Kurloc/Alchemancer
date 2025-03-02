from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, Union

from sqlalchemy import Connection

from alchemancer.reflection_handler import ReflectionHandler
from alchemancer.types.query import HqlQuery


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
    @abstractmethod
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
