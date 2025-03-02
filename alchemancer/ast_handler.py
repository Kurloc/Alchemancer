import ast
from typing import Any, Callable, Dict, Optional, Tuple, cast

from reflection_handler import (
    ReflectionHandler,
)
from sqlalchemy import Select

from alchemancer.types.query import (
    ColumnTypesT,
)


class AstHandler:
    reflection_handler: ReflectionHandler

    def __init__(self, reflection_handler: Optional[ReflectionHandler] = None) -> None:
        self.reflection_handler = reflection_handler or ReflectionHandler()

    def convert_ast_to_sqlalchemy_column(
        self, functional_column: str, context: Dict, model_key: Optional[str] = None
    ) -> (None | Select | ColumnTypesT | Callable[..., Any]) | (
        Tuple[str, Select | ColumnTypesT | Callable[..., Any]]
    ):
        # For now the return type is any but this honestly only returns sql alchemy columns / selects
        tokens = ast.parse(functional_column)
        bodies: list[ast.stmt] = tokens.body
        for body in bodies:
            return self._ast_switch(body.value, context, model_key)

    def _ast_switch(
        self, value, context: Dict, model_key: Optional[str] = None
    ) -> (None | Select | ColumnTypesT | Callable[..., Any]) | (
        Tuple[str, Select | ColumnTypesT | Callable[..., Any]]
    ):
        match type(value):
            case ast.Name:
                value = cast(ast.Name, value)
                return self._process_name(value, context, model_key)
            case ast.Constant:
                value = cast(ast.Constant, value)
                return value.value
            case ast.Call:
                value = cast(ast.Call, value)
                return self._process_call(value, context, model_key)
            case ast.Attribute:
                value = cast(ast.Attribute, value)
                return self._process_attribute(value, context, model_key)
            case ast.keyword:
                value = cast(ast.keyword, value)
                return self._process_keyword(value, context, model_key)

        raise NotImplementedError(f"Not implemented: {value}")

    def _process_name(
        self, name_obj: ast.Name, context: Dict, model_key: Optional[str] = None
    ):
        value = (
            context.get(name_obj.id)
            or self.reflection_handler.model_class_cache.get(name_obj.id)
            or self.reflection_handler.model_field_cache.get(model_key, {}).get(
                name_obj.id
            )
        )
        if value is None and name_obj.id.lower() not in ["none", "null"]:
            raise Exception("Could not find", name_obj.id)

        return value

    def _process_call(
        self, call_obj: ast.Call, context: Dict, model_key: Optional[str] = None
    ):
        processed_args = [
            self._ast_switch(x, context, model_key) for x in call_obj.args
        ]
        processed_keywords = {
            z[0]: z[1]
            for z in [
                self._ast_switch(x, context, model_key) for x in call_obj.keywords
            ]
        }
        processed_func: Callable = self._ast_switch(call_obj.func, context, model_key)
        return processed_func(*processed_args, **processed_keywords)

    def _process_attribute(
        self,
        attribute_obj: ast.Attribute,
        context: Dict,
        model_key: Optional[str] = None,
    ):
        parent = self._ast_switch(attribute_obj.value, context, model_key)
        return getattr(parent, attribute_obj.attr)

    def _process_keyword(
        self, keyword_obj: ast.keyword, context: Dict, model_key: Optional[str] = None
    ):
        return keyword_obj.arg, self._ast_switch(keyword_obj.value, context, model_key)

    @staticmethod
    def _process_constant(constant_obj: ast.Constant):
        return constant_obj.value
