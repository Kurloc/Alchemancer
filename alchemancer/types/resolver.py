from abc import ABCMeta, abstractmethod
from datetime import date, datetime, time
from typing import Any, Callable, Dict, List, Optional, Type, Union

from sqlalchemy import Column, Connection, Integer, MetaData, Select, Table

from alchemancer.types.query import NoOpConnection, PrimitiveT

ResolverParamTypesT = Union[PrimitiveT, date, time, datetime]


class HqlResolverParameter:
    optional: bool = False
    python_type: Type[PrimitiveT]
    default_value: Optional[ResolverParamTypesT | Callable[[], ResolverParamTypesT]] = None

    def __init__(
        self,
        python_type: Type[PrimitiveT],
        default_value: Optional[ResolverParamTypesT | Callable[[], ResolverParamTypesT]] = None,
        optional: bool = False,
    ):
        self.default_value = default_value
        self.python_type = python_type
        self.optional = optional


class HqlResolver(metaclass=ABCMeta):
    __table: Table | None
    __connection: Connection
    __execution_query: Select

    # user overrides / protected properties & methods
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, HqlResolverParameter]:
        return {}

    @property
    @abstractmethod
    def columns(self) -> Dict[str, Column]:
        return {}

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def table(self) -> Table:
        return self.__table

    @abstractmethod
    def _insert_data_hook(self, **kwargs) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def _execute_hook(self, **kwargs) -> Select:
        pass

    def __init__(
        self,
        connection: Optional[Connection] = None,
        **kwargs,
    ):
        self.__table = None
        self.__connection = connection

    # protected / internal methods, do not override
    def execute(self, **kwargs):
        print("is_live_connection", self.__is_live_connection)
        if self.__is_live_connection:
            for name, parameter in self.parameters.items():
                kwargs = self.__validate_parameter(name, parameter, **kwargs)

            # do data insert logic here
            self._insert_data(**kwargs)

        # execute the users execute logic so we can get a query
        self.__create_temp_table()
        self.__execution_query = self._execute_hook(**kwargs)

        return self.__execution_query

    def _insert_data(self, **kwargs) -> None:
        if self.__is_live_connection is False:
            return

        records = self._insert_data_hook(**kwargs)
        self.__insert_data_into_temp_table(records)

    def _convert_resolver_to_query(self):
        return self.execute(dry_run=True)

    # private properties & methods
    @property
    def __is_live_connection(self) -> bool:
        return (
            isinstance(self.__connection, NoOpConnection) or self.__connection is NoOpConnection
        ) is False

    def __create_temp_table(self):
        if self.__table is None:  # If table hasn't been created yet
            metadata = MetaData()
            self.__table = Table(
                f"TEMP__{str(__name__).upper().replace('.', '_')}",
                metadata,
                Column("pk_id", Integer, primary_key=True),
                *[column for column in self.columns],
                prefixes=["TEMPORARY"],
                # postgresql_on_commit='DROP',  # do we have to do this for each engine?
            )
            # Skip creating the table on noop connections
            if self.__is_live_connection is False:
                return self.__table

            # Create table with connection and return
            self.__table.create(self.__connection)
            return self.__table

    def __insert_data_into_temp_table(self, records: List[Dict[str, Any]]) -> None:
        self.__create_temp_table()
        self.__connection.execute(self.__table.insert().values(records))

    @staticmethod
    def __validate_parameter(
        name: str, parameter: HqlResolverParameter, **kwargs
    ) -> Dict[str, Any]:
        # param is required and there's no value
        if name not in kwargs.keys() and parameter.optional is False:
            raise Exception(f'parameter "{name}::{parameter.python_type}" is required')

        param_value = kwargs.get(name, parameter.default_value)
        param_value = param_value() if isinstance(param_value, Callable) else param_value
        kwargs[name] = param_value

        return kwargs
