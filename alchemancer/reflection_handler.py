import inspect
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Type, TypeVar, Union, cast

from marshmallow.fields import Boolean
from marshmallow.fields import Date as MarshmallowDate
from marshmallow.fields import DateTime as MarshmallowDateTime
from marshmallow.fields import Dict as MarshmallowDict
from marshmallow.fields import Float, Integer
from marshmallow.fields import List as MarshmallowList
from marshmallow.fields import String
from sqlalchemy.orm import DeclarativeBase

from alchemancer.types.marshmallow import JsonBField, JsonField
from alchemancer.types.query import ColumnTypesT
from alchemancer.types.resolver import HqlResolver

T = TypeVar("T")
_module = TypeVar("_module", bound=str)
_absolute_module_path = Union[Path, str]


class ReflectionHandler:
    """
    Static handler that is initialized once and reused
    """

    model_class_cache: Dict[str, Type[DeclarativeBase]] = {}
    model_field_cache: Dict[str, Dict[str, Type[ColumnTypesT]]] = {}
    python_primitive_types_to_marshmallow_fields = {
        int: Integer,
        float: Float,
        str: String,
        bool: Boolean,
        dict: MarshmallowDict,
        list: MarshmallowList,
        date: MarshmallowDate,
        datetime: MarshmallowDateTime,
        JsonBField: JsonBField,
        JsonField: JsonBField,
    }
    resolver_name_type_cache: Dict[str, Type[HqlResolver]] = {}

    @staticmethod
    def init(
        model_dir_module_paths: List[Tuple[_module, _absolute_module_path]],
        resolver_dir_module_paths: List[Tuple[_module, _absolute_module_path]] = None,
    ):
        """
        Loads and imports modules using a list of module names and paths

        This can be called multiple times consecutively if needed.

        :param resolver_dir_module_paths:
        :param model_dir_module_paths:
        :return:
        """
        resolver_dir_module_paths = resolver_dir_module_paths or []

        resolver_classes: List = []
        for module_set in resolver_dir_module_paths:
            resolver_classes.extend(
                list(
                    ReflectionHandler._import_objects_from_modules_via_path(
                        module_set[1], module_set[0], HqlResolver
                    )
                )
            )

        ReflectionHandler.resolver_name_type_cache = {}
        for resolver in resolver_classes:
            ReflectionHandler.resolver_name_type_cache[resolver().name] = resolver

        model_classes = []
        for module_set in model_dir_module_paths:
            model_classes.extend(
                list(
                    ReflectionHandler._import_objects_from_modules_via_path(
                        module_set[1], module_set[0]
                    )
                )
            )
        model_classes = cast(List[Type[DeclarativeBase]], model_classes)

        for _class in model_classes:
            if hasattr(_class, "__table__"):
                ReflectionHandler.model_class_cache[_class.__name__] = _class
                ReflectionHandler.model_field_cache[_class.__name__] = {}
                columns = _class.__table__.columns
                for _, column in columns.items():
                    ReflectionHandler.model_field_cache[_class.__name__][column.name] = column

    @staticmethod
    def _import_objects_from_modules_via_path(
        module_path: _absolute_module_path,
        module_name: str,
        type_to_import: T = None,
        excluded_dir_names: List[str] = None,
        check_subclasses_of_type: bool = True,
        return_instances=False,
    ) -> Set[T]:
        type_to_import = type_to_import or DeclarativeBase
        excluded_dir_names = excluded_dir_names or ["__pycache__"]
        class_set = set() if not return_instances else []
        module_path = os.path.abspath(module_path)
        dirs_to_walk = [_dir[0] for _dir in os.walk(module_path)]
        first_pass = True

        for dir_path in dirs_to_walk:
            if dir_path in excluded_dir_names:
                continue

            module_chain = module_name
            if not first_pass:
                module_chain = module_chain + str(dir_path).replace(os.sep, ".")

            files_in_dir = os.listdir(dir_path)
            files_to_import_from = [
                f[:-3] for f in files_in_dir if f.endswith(".py") and f != "__init__.py"
            ]

            objects_to_possibly_import = []
            for file in files_to_import_from:
                # @TODO: There is a bug here where the path is incorrect when recursing directories
                files_module_name = f"{module_chain}.{file}"
                _modules_to_import = [
                    __import__(files_module_name, fromlist=[f"{dir_path}{os.sep}{file}"])
                ]

                for __module in _modules_to_import:
                    items_to_import = dir(__module)
                    for item in items_to_import:
                        if "__" in item:
                            continue

                        objects_to_possibly_import.append(getattr(__module, item))

            for _object in objects_to_possibly_import:
                if check_subclasses_of_type:
                    if hasattr(_object, "__mro__"):
                        base_classes = inspect.getmro(_object)[1:-1]
                        if type_to_import in base_classes:
                            if not return_instances:
                                class_set.add(_object)
                                setattr(
                                    sys.modules[__name__],
                                    type_to_import.__name__,
                                    type_to_import,
                                )
                            else:
                                class_set.append(_object)
                else:
                    if isinstance(_object, type_to_import):
                        if not return_instances:
                            class_set.add(_object)
                            setattr(
                                sys.modules[__name__], type_to_import.__name__, type_to_import
                            )
                        else:
                            class_set.append(_object)

            first_pass = False

        return class_set
