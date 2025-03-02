import ast
from typing import Optional, Dict, Any, List, Tuple, Type, Callable, Union, cast

import marshmallow
from sqlalchemy import Select, and_, or_, case, Engine, Connection
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql._typing import _ColumnExpressionArgument
from sqlalchemy.sql.functions import array_agg, coalesce
from sqlalchemy.sql.operators import (
    is_,
    is_not,
    like_op,
    not_like_op,
    not_ilike_op,
    regexp_match_op,
)

from alchemancer.alchemancer_types import (
    HqlQuery,
    HqlSelect,
    WhereClausT,
    HqlJoin,
    ColumnListT,
    GeneratedQuery,
    NoOpConnection,
)
from alchemancer.sqlalchemy.reflection_handler import (
    ReflectionHandler,
)


class QueryGenerator:
    _engine: Engine
    reflection_handler = ReflectionHandler
    base_context_dict: Dict[str, Any]

    def __init__(self, engine, base_context_dict: Dict[str, Any] = None):
        self.base_context_dict = {
            "array_agg": array_agg,
            "coalesce": coalesce,
            **(base_context_dict or {})
        }
        self._engine = engine

    def return_from_hql_query(self, query: HqlQuery):
        context_dict = {**self.base_context_dict}
        with self._engine.connect() as connection:
            generated_query = self._process_query(query, context_dict, connection)
            response = connection.execute(generated_query.query).fetchall()

        schema_dict = {}
        for x in generated_query.query.columns:
            python_type = x.type.python_type
            is_many = False
            if python_type == list:
                is_many = True
                python_type = x.type.item_type.python_type

            marshmallow_field = (
                self.reflection_handler.python_primitive_types_to_marshmallow_fields[
                    python_type
                ]
            )
            schema_dict[x.name] = (
                marshmallow.fields.List(marshmallow_field())
                if is_many
                else marshmallow_field()
            )

        schema = marshmallow.Schema.from_dict(fields=schema_dict)(many=True)
        return schema.dump(response)

    def _process_query(
        self,
        query: HqlQuery,
        context_dict: Optional[Dict] = None,
        connection: Optional[Connection] = NoOpConnection,
    ):
        selected_join_columns, join_conditions = None, None
        context_dict = context_dict or {**self.base_context_dict}

        select = query["select"]
        joins = query.get("joins")
        where = query.get("where")
        having = query.get("having")
        limit = query.get("limit")
        offset = query.get("offset")
        order_by = query.get("order_by")
        group_by = query.get("group_by")
        distinct = query.get("distinct")
        subqueries = query.get("subqueries")

        if subqueries:
            self._process_sub_queries(subqueries, context_dict, connection)

        if joins:
            selected_join_columns, join_conditions = self._process_joins(joins, context_dict)

        query = self._process_selects(
            select, context_dict, selected_join_columns, join_conditions
        )
        if having:
            query = query.having(*self._process_where_clause(having, context_dict))

        if where:
            query = query.filter(*self._process_where_clause(where, context_dict))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if distinct:
            query = query.distinct()

        if group_by:
            group_by_columns = []
            for column in group_by:
                split_key = column.split(".")
                model_name = split_key[0]
                field_name = split_key[1]
                group_by_columns.append(
                    self.reflection_handler.model_field_cache[model_name][field_name]
                )

            query = query.group_by(*group_by_columns)

        if order_by:
            order_by_columns = {}
            for column in order_by:
                value = order_by[column]
                split_key = column.split(".")
                model_name = split_key[0]
                field_name = split_key[1]
                if value["dir"] == "desc":
                    order_by_columns[value["index"]] = (
                        self.reflection_handler.model_field_cache[model_name][
                            field_name
                        ].desc()
                    )
                else:
                    order_by_columns[value["index"]] = (
                        self.reflection_handler.model_field_cache[model_name][
                            field_name
                        ].asc()
                    )

            order_by_array = []
            keys_len = len(order_by_columns)
            for idx in range(keys_len):
                order_by_array.append(order_by_columns[idx])

            query = query.order_by(*order_by_array)

        return GeneratedQuery(query, limit, offset)

    def _process_sub_queries(
        self,
        subqueries: Dict[str, HqlQuery],
        context_dict: Optional[Dict] = None,
        connection: Optional[Connection] = NoOpConnection,
    ):
        # @TODO, JSON key order is not deterministic
        # so we need to sort the keys
        # unless we can guarantee the order, which seems like a crap shoot since it's up to the JSON implementation
        # which may be different across web frameworks
        context_dict["subqueries"] = {}
        for subquery_name in subqueries:
            subquery = subqueries[subquery_name]
            processed_subquery = self._process_query(subquery, context_dict, connection)
            context_dict["subqueries"][
                subquery_name
            ] = processed_subquery.query.subquery()

    def _process_selects(
        self,
        select: Dict[str, Dict[str, HqlSelect]],
        context_dict: Dict,
        join_columns: Optional[List[ColumnListT]] = None,
        joins_conditions: Optional[
            List[Tuple[Type[DeclarativeBase], List[_ColumnExpressionArgument[bool]]]]
        ] = None,
    ):
        models = []
        select_columns = []
        for model_key in select.keys():
            model_or_subquery = self.reflection_handler.model_class_cache.get(
                model_key, None
            )
            if model_or_subquery is None:
                model_or_subquery = context_dict.get("subqueries", {}).get(
                    model_key, None
                )

            if model_or_subquery is None:
                raise Exception("we need something here!")

            models.append(model_or_subquery)
            columns = select[model_key]
            for column_key in columns.keys():
                column_info: HqlSelect = columns[column_key]
                label_name = column_info.get("label")
                is_distinct = column_info.get("distinct")
                else_ = column_info.get("else_", None)

                if else_ is not None:
                    else_ = self._return_value_from_hql_select_or_string(else_, context_dict)

                if when_thens := column_info.get("whens", []):
                    when_then_conditions = []
                    for when_item in when_thens:
                        when = self._process_where_clause(when_item["when"], context_dict)
                        then = self._return_value_from_hql_select_or_string(
                            when_item["then"], context_dict
                        )
                        when_then_conditions.append((when, then))

                    select_column = case(*when_then_conditions, else_=else_).label(label_name or column_key)
                    if is_distinct:
                        select_column = select_column.distinct()

                else:
                    select_column = self._return_value_from_hql_select_or_string(
                        column_info, context_dict, model_key, column_key
                    )

                select_columns.append(select_column)

        need_to_select_from = False
        if len(select_columns) == 0:
            need_to_select_from = True

        if join_columns:
            select_columns.extend(join_columns)

        query = Select(*select_columns)

        if need_to_select_from:
            query = query.select_from(*models)

        if joins_conditions:
            for join in joins_conditions:
                query = query.join(join[0], *join[1])

        return query

    def _process_where_clause(
        self, where: WhereClausT, context_dict: Dict
    ) -> List[_ColumnExpressionArgument[bool]]:
        keys = where.keys()
        clauses = []
        for key in keys:
            lower_cased_key = key.lower()
            if lower_cased_key == "and":
                value = where[key]
                clauses.append(
                    and_(
                        *self._process_where_clause(value, context_dict),
                    )
                )
            elif lower_cased_key == "or":
                value = where[key]
                or_clause_input = []
                for or_dict in value:
                    or_clause_input.extend(self._process_where_clause(or_dict, context_dict))

                clauses.append(or_(*or_clause_input))
            else:
                model_name, field_name, operation = (
                    self._parse_column_name_and_operation_from_key(key)
                )
                is_subquery = False
                model_or_subquery = self.reflection_handler.model_class_cache.get(
                    model_name, None
                )
                if model_or_subquery is None:
                    model_or_subquery = context_dict.get("subqueries", {}).get(
                        model_name, None
                    )
                    is_subquery = model_or_subquery is not None

                if model_or_subquery is None:
                    raise Exception("we need something here!")

                if is_subquery:
                    column = getattr(model_or_subquery.c, field_name)
                else:
                    column = self.reflection_handler.model_field_cache[model_name][
                            field_name
                    ]

                clauses.append(
                    operation(
                        column,
                        self._return_value_from_hql_select_or_string(where[key], context_dict),
                    )
                )

        return clauses

    def _process_joins(self, joins: Dict[str, HqlJoin], context_dict: Dict) -> Tuple[
        List[ColumnListT],
        List[Tuple[Type[DeclarativeBase], List[_ColumnExpressionArgument[bool]]]],
    ]:
        select_columns = []
        joins_to_return = []
        for join_key in joins.keys():
            columns = joins[join_key].get("select")
            model = self.reflection_handler.model_class_cache[join_key]
            where_clauses = self._process_where_clause(joins[join_key].get("where"), context_dict)
            for column_key in columns.keys():
                column_info = columns[column_key]
                select_column = self.reflection_handler.model_field_cache[join_key][
                    column_key
                ]
                if column_info.get("label"):
                    select_column = select_column.label(column_info["label"])
                else:
                    select_column = select_column.label(
                        f"{join_key.lower()}_{column_key}"
                    )
                if column_info.get("distinct"):
                    select_column = select_column.distinct()

                select_columns.append(select_column)

            joins_to_return.append((model, where_clauses))

        return select_columns, joins_to_return

    def _build_ast_tokens(
        self, functional_column: str, context: Dict, model_key: Optional[str] = None
    ) -> Any:  # For now the return type is any but this honestly only returns sql alchemy columns / selects
        tokens = ast.parse(functional_column)
        for body in tokens.body:
            return self.type_monster(body.value, context, model_key)

    def type_monster(self, value, context: Dict, model_key: Optional[str] = None):
        match type(value):
            case ast.Name:
                value = cast(ast.Name, value)
                return self.process_name(value, context, model_key)
            case ast.Constant:
                value = cast(ast.Constant, value)
                return self.process_constant(value, context, model_key)
            case ast.Call:
                value = cast(ast.Call, value)
                return self.process_call(value, context, model_key)
            case ast.Attribute:
                value = cast(ast.Attribute, value)
                return self.process_attribute(value, context, model_key)

        raise Exception('ooof not implemented', value, context)

    def process_name(self, name_obj: ast.Name, context: Dict, model_key: Optional[str] = None):
        x = (
                context.get(name_obj.id)
            or self.reflection_handler.model_class_cache.get(name_obj.id)
            or self.reflection_handler.model_field_cache.get(model_key, {}).get(name_obj.id)
        )
        if x is None and name_obj.id.lower() not in ['none', 'null']:
            raise Exception('Could not find', name_obj.id)
        return x

    def process_constant(self, constant_obj: ast.Constant, context: Dict, model_key: Optional[str] = None):
        return constant_obj.value

    def process_call(self, call_obj: ast.Call, context: Dict, model_key: Optional[str] = None):
        processed_args = [self.type_monster(x, context, model_key) for x in call_obj.args]
        processed_keywords = {x: self.type_monster(x, context, model_key) for x in call_obj.keywords}
        processed_func =  self.type_monster(call_obj.func, context, model_key)
        return processed_func(*processed_args, **processed_keywords)

    def process_attribute(self, attribute_obj: ast.Attribute, context: Dict, model_key: Optional[str] = None):
        parent = self.type_monster(attribute_obj.value, context, model_key)
        return getattr(parent, attribute_obj.attr)

    def _return_value_from_hql_select_or_string(
        self,
        select: Union[str, HqlSelect],
        context_dict: Dict,
        model_key: Optional[str] = None,
        column_name: Optional[str] = None,
    ) -> Any:
        if isinstance(select, str):
            if "(" in select and ")" in select:
                return self._build_ast_tokens(select, context_dict, model_key)
            if "." not in select:
                return select

            key_split = select.split(".")
            model_name = key_split[0]
            action_split = key_split[1].split("__")
            field_name = action_split[0]
            possible_value = self.reflection_handler.model_field_cache.get(
                model_name, {}
            ).get(field_name, None)
            if possible_value is not None:
                return possible_value
            else:
                return select
        elif isinstance(select, Dict):
            label = select.get("label", None)
            if "value" in select.keys():
                value = self._return_value_from_hql_select_or_string(select.get("value"), context_dict)
                is_distinct = select.get("distinct", None) is not None
                if label is not None:
                    value = value.label(label)
                if is_distinct:
                    value = value.distinct()
                return value

            if "(" in column_name and ")" in column_name:
                select = self._build_ast_tokens(column_name, context_dict, model_key)
                if label is not None:
                    select = select.label(label)
                return select

            if (model_obj := self.reflection_handler.model_field_cache.get(model_key, None)) is not None:
                if '[' and ']' in column_name:
                    split_items = column_name.split("[")
                    column_name = split_items[0]
                    select = model_obj[column_name]
                    split = [x.replace("'", "").replace("]", "") for x in split_items[1:]]
                    for item in split:
                        select = select[item]
                else:
                    select = model_obj[column_name]

                if label is not None:
                    select = select.label(label)
                return select

            model_or_subquery = context_dict.get("subqueries", {}).get(
                model_key, None
            )
            if model_or_subquery is not None:
                select = getattr(model_or_subquery.c, column_name)
                if label is not None:
                    select = select.label(label)
                return select

            raise Exception("Not implemented yet for type", type(select))
        elif type(select) in [
            int,
            str,
            float,
            bool,
            List[int],
            List[str],
            List[float],
            List[bool],
        ]:
            return select
        else:
            raise Exception("Not implemented yet for type", type(select))

    @staticmethod
    def _get_operation_from_action_name(operation: str):
        operation = operation.lower()
        if operation == "eq":
            return lambda comparator, _value: (
                is_ if isinstance(_value, bool) else comparator == _value
            )

        if operation == "ne":
            return lambda comparator, _value: (
                is_not if isinstance(_value, bool) else comparator != _value
            )

        if operation == "like":
            return like_op

        if operation == "not_like":
            return not_like_op

        if operation == "not_ilike":
            return not_ilike_op

        if operation == "lt":
            return lambda comparator, _value: comparator < _value

        if operation == "lte":
            return lambda comparator, _value: comparator <= _value

        if operation == "gt":
            return lambda comparator, _value: comparator > _value

        if operation == "gte":
            return lambda comparator, _value: comparator >= _value

        if operation == "re":
            return regexp_match_op

        if operation == "not_re":
            return

    @staticmethod
    def _parse_column_name_and_operation_from_key(key: str) -> Tuple[str, str, Callable]:
        key_split = key.split(".")
        model_name = key_split[0]
        action_split = key_split[1].split("__")
        field_name = action_split[0]
        operation = QueryGenerator._get_operation_from_action_name(action_split[1])
        return model_name, field_name, operation
