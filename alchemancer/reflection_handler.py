import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Type, TypeVar, Union, cast

from marshmallow.fields import Boolean, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase

from alchemancer.types.marshmallow import JsonBField, JsonField
from alchemancer.types.query import ColumnTypesT
from alchemancer.types.resolver import HqlResolver

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
        dict: Dict,
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

        :param model_dir_module_paths:
        :return:
        """
        resolver_dir_module_paths = resolver_dir_module_paths or []

        resolver_classes: List = []
        for module_set in resolver_dir_module_paths:
            resolver_classes.extend(
                list(
                    ReflectionHandler._import_modules_from_path(
                        module_set[1], module_set[0], [HqlResolver]
                    )
                )
            )

        ReflectionHandler.resolver_name_type_cache = {}
        for resolver in resolver_classes:
            print("resolver.name:", resolver().name, resolver)
            ReflectionHandler.resolver_name_type_cache[resolver().name] = resolver

        model_classes = []
        for module_set in model_dir_module_paths:
            model_classes.extend(
                list(ReflectionHandler._import_modules_from_path(module_set[1], module_set[0]))
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
    def _import_modules_from_path(
        module_path: _absolute_module_path,
        module_name: str,
        types_to_import: List[Type] = None,
        excluded_dir_names: List[str] = None,
        check_subclasses_of_type: bool = True,
        return_instances=False,
    ) -> Set[Type[Any]]:
        types_to_import = types_to_import or [DeclarativeBase]
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
                        for _type in types_to_import:
                            if _type in base_classes:
                                if not return_instances:
                                    class_set.add(_object)
                                    setattr(sys.modules[__name__], _type.__name__, _type)
                                else:
                                    class_set.append(_object)
                else:
                    for _type in types_to_import:
                        if isinstance(_object, _type):
                            if not return_instances:
                                class_set.add(_object)
                                setattr(sys.modules[__name__], _type.__name__, _type)
                            else:
                                class_set.append(_object)

            first_pass = False

        return class_set
