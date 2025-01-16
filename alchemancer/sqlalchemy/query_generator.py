import ast
from _ast import Call, Attribute, Constant
from typing import Optional, Dict, Any, List, Tuple, Type, Callable, Union

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

from alchemancer.types import (
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
        self.base_context_dict = base_context_dict or {
            "array_agg": array_agg,
            "coalesce": coalesce,
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
            self.process_sub_queries(subqueries, context_dict, connection)

        if joins:
            selected_join_columns, join_conditions = self.process_joins(joins, context_dict)

        query = self.process_selects(
            select, context_dict, selected_join_columns, join_conditions
        )
        if having:
            query = query.having(*self.process_where_clause(having, context_dict))

        if where:
            query = query.filter(*self.process_where_clause(where, context_dict))

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

    def process_sub_queries(
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

    def process_selects(
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
            is_subquery = False
            model_or_subquery = self.reflection_handler.model_class_cache.get(
                model_key, None
            )
            if model_or_subquery is None:
                model_or_subquery = context_dict.get("subqueries", {}).get(
                    model_key, None
                )
                is_subquery = model_or_subquery is not None

            if model_or_subquery is None:
                raise Exception("we need something here!")

            models.append(model_or_subquery)
            columns = select[model_key]
            for column_key in columns.keys():
                column_info: HqlSelect = columns[column_key]
                label_name = column_info.get("label")
                is_distinct = column_info.get("distinct")
                else_ = column_info.get("else_", None)

                if "(" and ")" in column_key:
                    select_column = self._build_ast_tokens(column_key, model_key)
                    select_columns.append(select_column.label(label_name or column_key))
                    continue

                if isinstance(column_info, str):
                    select_column = self.return_value_from_hql_select_or_string(
                        column_info
                    )
                    select_columns.append(select_column.label(column_key))
                    continue

                if else_ is not None:
                    else_ = self.return_value_from_hql_select_or_string(else_)

                if when_thens := column_info.get("whens", []):
                    when_then_conditions = []
                    for when_item in when_thens:
                        # WHENs
                        # loop key to get model, column & operation
                        when = self.process_where_clause(when_item["when"], context_dict)
                        then = self.return_value_from_hql_select_or_string(
                            when_item["then"]
                        )

                        # Then use value of dict for value,
                        # need to process this for literal value or column / function being passed

                        #
                        # THENs
                        # check value for column selection / function usage and if not treat as literal value
                        when_then_conditions.append((when, then))

                    select_column = case(*when_then_conditions, else_=else_)
                else:
                    if not is_subquery:
                        select_column = self.reflection_handler.model_field_cache[
                            model_key
                        ][column_key]
                    else:
                        select_column = getattr(model_or_subquery.c, column_key)

                    if label_name is not None:
                        select_column = select_column.label(label_name)
                    if is_distinct:
                        select_column = select_column.distinct()

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

    def process_where_clause(
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
                        *self.process_where_clause(value, context_dict),
                    )
                )
            elif lower_cased_key == "or":
                value = where[key]
                or_clause_input = []
                for or_dict in value:
                    or_clause_input.extend(self.process_where_clause(or_dict, context_dict))

                clauses.append(or_(*or_clause_input))
            else:
                model_name, field_name, operation = (
                    self.parse_column_name_and_operation_from_key(key)
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
                        self.return_value_from_hql_select_or_string(where[key]),
                    )
                )

        return clauses

    def process_joins(self, joins: Dict[str, HqlJoin], context_dict: Dict) -> Tuple[
        List[ColumnListT],
        List[Tuple[Type[DeclarativeBase], List[_ColumnExpressionArgument[bool]]]],
    ]:
        select_columns = []
        joins_to_return = []
        for join_key in joins.keys():
            columns = joins[join_key].get("select")
            model = self.reflection_handler.model_class_cache[join_key]
            where_clauses = self.process_where_clause(joins[join_key].get("where"), context_dict)
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

    def _build_ast_tokens(
        self, functional_column: str, model_key: Optional[str] = None
    ) -> Any:  # For now the return type is any but this honestly only returns sql alchemy columns / selects
        tokens = ast.parse(functional_column)
        print(tokens)

        # reverse recurse
        # get to bottom
        lowest_node = None
        for body in tokens.body:
            return self._recurse_ast_bodies(body, model_key)

    def _recurse_ast_bodies(self, body, model_key: Optional[str] = None):
        is_there_a_value = getattr(body, "value", None)

        print("body", body)
        # if there is go deeper
        if is_there_a_value:
            x = body.value
            has_args = getattr(x, "args", None)
            outer_func = getattr(x, "func", None)
            outer_func_args = []
            if has_args:
                for arg in has_args:
                    print("arg loop", arg)
                    need_to_drill_deeper_bool = isinstance(arg, Call)
                    if need_to_drill_deeper_bool:
                        need_to_drill_deeper = arg
                        self.pull_value_out(need_to_drill_deeper, outer_func_args)
                    elif hasattr(arg, "value") and isinstance(arg.value, ast.Name):
                        print("HIT:", arg.value.id, ".", arg.attr)
                        outer_func_args.append(
                            self.reflection_handler.model_field_cache[
                                str(arg.value.id)
                            ][str(arg.attr)]
                        )
                    else:
                        print(arg)
                        if not hasattr(arg, "value") and model_key is not None:
                            arg_value = self.reflection_handler.model_field_cache[
                                model_key
                            ].get(arg.id, None)
                            if arg_value is not None:
                                outer_func_args.append(arg_value)
                        else:
                            outer_func_args.append(arg.value)

            if outer_func:
                print("need to execute this: ", outer_func.id)
                outer_func_inst = self.base_context_dict[outer_func.id](
                    *outer_func_args
                )
                print("outer_func_inst", outer_func_inst)
                return outer_func_inst
        else:
            print("hmmm what do now?", body)

    def pull_value_out(self, need_to_drill_deeper, outer_func_args):
        print("pull_value_out", need_to_drill_deeper)
        if isinstance(need_to_drill_deeper, Constant):
            outer_func_args.append(need_to_drill_deeper.value)
            return

        function_name = need_to_drill_deeper.func.id
        function_instance = self.base_context_dict[function_name]

        args = []
        for arg in need_to_drill_deeper.args:
            need_to_build_value = isinstance(arg, Attribute)
            if need_to_build_value:
                class_name = arg.value.id
                field_name = arg.attr
                built_value = self.reflection_handler.model_field_cache[class_name][
                    field_name
                ]
                args.append(built_value)
            else:
                self.pull_value_out(arg, args)
                print("RING A DING DING")

        prepped_value = function_instance(*args)
        outer_func_args.append(prepped_value)
        print("prepped_value", prepped_value)

    @staticmethod
    def parse_column_name_and_operation_from_key(key: str) -> Tuple[str, str, Callable]:
        key_split = key.split(".")
        model_name = key_split[0]
        action_split = key_split[1].split("__")
        field_name = action_split[0]
        operation = QueryGenerator._get_operation_from_action_name(action_split[1])
        return model_name, field_name, operation

    def return_value_from_hql_select_or_string(self, select: Union[str, HqlSelect]):
        if isinstance(select, str):
            if "(" and ")" in select:
                return self._build_ast_tokens(select)
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
            if "value" in select.keys():
                value = self.return_value_from_hql_select_or_string(select.get("value"))
                label = select.get("label", None)
                is_distinct = select.get("distinct", None) is not None
                if label is not None:
                    value = value.label(label)
                if is_distinct:
                    value = value.distinct()
                return value
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
