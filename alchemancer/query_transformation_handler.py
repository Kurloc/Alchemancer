from typing import (
    Dict,
    Literal,
    Optional,
    Self,
    TypeAlias,
    Union,
    cast,
)

from alchemancer.types.query import HqlJoin, HqlQuery, HqlSelect, HqlSort, WhereClausT

TransformationName: TypeAlias = str


class DebugNode:
    alias: str
    html_alias: str
    str_alias: str

    def __init__(
        self, alias: str = "debug", html_alias: str = "html", str_alias: str = "str"
    ) -> None:
        self.alias = alias
        self.html_alias = html_alias
        self.str_alias = str_alias


class AliasNode:
    alias: str

    def __init__(self, alias: str = "alias") -> None:
        self.alias = alias


class LimitNode:
    alias: str

    def __init__(self, alias: str = "limit") -> None:
        self.alias = alias


class OffsetNode:
    alias: str

    def __init__(self, alias: str = "offset") -> None:
        self.alias = alias


class DistinctNode:
    alias: str

    def __init__(self, alias: str = "distinct") -> None:
        self.alias = alias


class GroupByNode:
    alias: str

    def __init__(self, alias: str = "group_by") -> None:
        self.alias = alias


class SortItemNode:
    index_alias: str
    nulls_last_alias: str
    dir_alias: str
    asc_alias: str
    desc_alias: str

    def __init__(
        self,
        index_alias: str = "index",
        nulls_last_alias: str = "nulls_last",
        dir_alias: str = "dir",
        asc_alias: str = "asc",
        desc_alias: str = "desc",
    ) -> None:
        self.index_alias = index_alias
        self.nulls_last_alias = nulls_last_alias
        self.dir_alias = dir_alias
        self.asc_alias = asc_alias
        self.desc_alias = desc_alias


class OrderByNode:
    alias: str
    sort_node: SortItemNode

    def __init__(self, sort_node: SortItemNode, alias: str = "order_by") -> None:
        self.alias = alias
        self.sort_node = sort_node


class ResolverArgsNode:
    alias: str

    def __init__(self, alias: str = "resolver_args") -> None:
        self.alias = alias


class HqlCTENode:
    name_alias: str
    recursive_alias: str

    def __init__(self, name_alias: str = "name", recursive_alias: str = "recursive") -> None:
        self.name_alias = name_alias
        self.recursive_alias = recursive_alias


class HqlUnionNode:
    alias: str
    name_alias: str
    left_alias: str
    right_alias: str
    cte_alias: str
    cte_node: HqlCTENode
    left_node: "QueryTransformation"
    right_node: "QueryTransformation"

    def __init__(
        self,
        alias: str = "union",
        name_alias: str = "name",
        left_alias: str = "left",
        right_alias: str = "right",
        cte_alias: str = "cte",
        cte_node: HqlCTENode = None,
        left_node: "QueryTransformation" = None,
        right_node: "QueryTransformation" = None,
    ) -> None:
        self.alias = alias
        self.name_alias = name_alias
        self.left_alias = left_alias
        self.right_alias = right_alias
        self.left_node = left_node
        self.right_node = right_node
        self.cte_alias = cte_alias
        self.cte_node = cte_node


class WhereClauseNode:
    alias: str

    def __init__(
        self,
        alias: str = "where",
    ) -> None:
        self.alias = alias


class HavingClauseNode:
    alias: str

    def __init__(self, alias: str = "having") -> None:
        self.alias = alias


class FilterNode:
    """Handled to abstract over the shared logic of the where and having clauses"""

    or_alias: str
    and_alias: str
    operator_map: Dict[str, str]

    def __init__(
        self,
        or_alias: str = "or",
        and_alias: str = "and",
        operator_map: Dict[str, str] = None,
    ) -> None:
        self.or_alias = or_alias
        self.and_alias = and_alias
        self.operator_map = operator_map or {}


class WhenThenNode:
    when_alias: str
    then_alias: str

    def __init__(self, when_alias: str = "when", then_alias: str = "then") -> None:
        self.when_alias = when_alias
        self.then_alias = then_alias


class SelectNode:
    alias: str
    label_alias: str
    value_alias: str
    distinct_alias: str
    whens_alias: str
    else_alias: str
    when_node: WhenThenNode
    else_node: Self
    select_node: Self
    select_alias: str
    where_alias: str

    def __init__(
        self,
        when_node: WhenThenNode,
        alias: str = "select",
        label_alias: str = "label",
        value_alias: str = "value",
        distinct_alias: str = "distinct",
        whens_alias: str = "whens",
        else_alias: str = "else_",
        select_alias: str = "select",
        where_alias: str = "where",
    ):
        self.alias = alias
        self.label_alias = label_alias
        self.value_alias = value_alias
        self.distinct_alias = distinct_alias
        self.whens_alias = whens_alias
        self.else_alias = else_alias
        self.select_alias = select_alias
        self.where_alias = where_alias
        self.when_node = when_node
        self.else_node = self
        self.select_node = self


class JoinNode:
    alias: str
    select_node: SelectNode = None
    where_node: WhereClauseNode = None

    def __init__(
        self,
        alias: str = "joins",
        where_node: WhereClauseNode = None,
        select_node: SelectNode = None,
    ) -> None:
        self.alias = alias
        if select_node is not None:
            self.select_node = select_node
        if where_node is not None:
            self.where_node = where_node


class QueryTransformation:
    select: SelectNode
    joins: JoinNode
    where: WhereClauseNode
    having: HavingClauseNode
    filter_info: FilterNode
    limit: LimitNode
    offset: OffsetNode
    order_by: OrderByNode
    group_by: GroupByNode
    distinct: DistinctNode
    subqueries: "QueryTransformation"
    cte: HqlCTENode
    union: HqlUnionNode
    union_all: HqlUnionNode
    resolver_args: ResolverArgsNode
    debug: DebugNode

    def __init__(
        self,
        select: SelectNode,
        joins: JoinNode,
        where: WhereClauseNode,
        having: HavingClauseNode,
        filter_info: FilterNode,
        limit: LimitNode,
        offset: OffsetNode,
        order_by: OrderByNode,
        group_by: GroupByNode,
        distinct: DistinctNode,
        cte: HqlCTENode,
        union: HqlUnionNode,
        union_all: HqlUnionNode,
        resolver_args: ResolverArgsNode,
        debug: DebugNode,
    ) -> None:
        if joins.select_node is None:
            joins.select_node = select
        if joins.where_node is None:
            joins.where_node = where

        union.left_node = self
        union.right_node = self
        union.cte_node = cte

        self.select = select
        self.joins = joins
        self.where = where
        self.having = having
        self.filter_info = filter_info
        self.limit = limit
        self.offset = offset
        self.order_by = order_by
        self.group_by = group_by
        self.distinct = distinct
        self.subqueries = self
        self.cte = cte
        self.union = union
        self.union_all = union_all
        self.resolver_args = resolver_args
        self.debug = debug


class QueryTransformationHandler:
    _transformations: Dict[TransformationName, QueryTransformation]

    def __init__(self, transformations: Dict[TransformationName, QueryTransformation]) -> None:
        self._transformations = transformations

    def transform_query(self, hql_query: Dict) -> HqlQuery:
        # This method should implement the logic to transform the HQL query
        # using the transformations defined in self._transformations
        target_transformation = self.find_transformation(hql_query)
        if target_transformation is None:
            return hql_query

        # select
        return_query: HqlQuery = {
            # can the cast be removed? Maybe if we go to pydantic models instead of typedDicts
            "select": cast(
                Dict[str, Dict[str, HqlSelect]],
                self._process_selects_for_models(hql_query, target_transformation),
            )
        }

        # joins
        if joins := hql_query.get(target_transformation.joins.alias):
            prepped_joins = {}
            if not isinstance(joins, Dict):
                raise TypeError("joins needs to be a Dict[str, HqlJoin]")

            for model_name, join_query in joins.items():
                prepped_joins[model_name] = self._process_select_transformation(
                    join_query,
                    target_transformation.joins.select_node.select_alias,
                    target_transformation,
                )
                prepped_joins[model_name]["where"] = self._process_filter_transformation(
                    join_query[target_transformation.joins.where_node.alias],
                    target_transformation,
                )

            return_query["joins"] = cast(Dict[str, HqlJoin], prepped_joins)

        # limit
        if limit := hql_query.get(target_transformation.limit.alias):
            if not isinstance(limit, int):
                raise TypeError("limit needs to be an int")

            return_query["limit"] = limit

        # offset
        if offset := hql_query.get(target_transformation.offset.alias):
            if not isinstance(offset, int):
                raise TypeError("offset needs to be an int")

            return_query["offset"] = offset

        # distinct
        if distinct := hql_query.get(target_transformation.distinct.alias):
            if not (
                isinstance(distinct, list)
                and all(isinstance(item, str) for item in distinct)
                or isinstance(distinct, bool)
            ):
                raise TypeError("distinct needs to be a List[str] or bool")

            return_query["distinct"] = distinct

        # group_by
        if group_by := hql_query.get(target_transformation.group_by.alias):
            if not (
                isinstance(group_by, list)
                and all(isinstance(group_by_item, str) for group_by_item in group_by)
            ):
                raise TypeError("group_by needs to be a List[str] or bool")

            return_query["group_by"] = group_by

        # debug
        if debug := hql_query.get(target_transformation.debug.alias):
            debug_value: Optional[Literal["html", "str"]] = None
            if debug == target_transformation.debug.html_alias:
                debug_value = "html"
            if debug == target_transformation.debug.str_alias:
                debug_value = "str"

            if debug_value is not None:
                return_query["debug"] = debug_value

        # order_by
        if order_by := hql_query.get(target_transformation.order_by.alias):
            return_order_by = {}
            for key, value in order_by.items():
                nulls_last = value.get(
                    target_transformation.order_by.sort_node.nulls_last_alias, None
                )
                order_direction = value.get(target_transformation.order_by.sort_node.dir_alias)
                if order_direction == target_transformation.order_by.sort_node.asc_alias:
                    order_direction = "asc"
                if order_direction == target_transformation.order_by.sort_node.desc_alias:
                    order_direction = "desc"

                updated_order_by_item = {
                    "index": value.get(target_transformation.order_by.sort_node.index_alias),
                    "dir": order_direction,
                }
                if nulls_last is not None:
                    updated_order_by_item["nulls_last"] = nulls_last

                return_order_by[key] = updated_order_by_item

            if not isinstance(return_order_by, Dict):
                raise TypeError("order_by needs to be a Dict[str, HqlSort]")

            return_query["order_by"] = cast(Dict[str, HqlSort], return_order_by)

        # where clause
        return_query["where"] = self._process_filter_transformation(
            hql_query.get(target_transformation.where.alias, {}), target_transformation
        )
        if len(return_query["where"].keys()) == 0:
            return_query.pop("where")

        # having clause
        return_query["having"] = self._process_filter_transformation(
            hql_query.get(target_transformation.having.alias, {}), target_transformation
        )
        if len(return_query["having"].keys()) == 0:
            return_query.pop("having")

        return return_query

    def _process_selects_for_models(
        self, hql_query, target_transformation
    ) -> Dict[str, Dict[str, HqlSelect]]:
        select = hql_query[target_transformation.select.alias]
        prepped_select: Dict[str, Dict[str, HqlSelect]] = {}
        for model_name, model_query in select.items():
            prepped_select[model_name] = {}
            for column_name, column_query in model_query.items():
                prepped_select[model_name][column_name] = self._process_select_transformation(
                    column_query, target_transformation.select.alias, target_transformation
                )

        return prepped_select

    def _process_select_transformation(
        self, column_query, select_alias: str, target_transformation
    ) -> Union[str, HqlSelect]:
        if isinstance(column_query, str):
            return column_query

        inner_select_node = column_query.get(select_alias)
        prepped_inner_select_node = {}
        if isinstance(inner_select_node, str):
            prepped_inner_select_node = inner_select_node
        elif inner_select_node is not None:
            for inner_select_key, inner_select_value in inner_select_node.items():
                prepped_inner_select_node[inner_select_key] = (
                    self._process_select_transformation(
                        inner_select_value, select_alias, target_transformation
                    )
                )

        updated_column_query = {
            "label": column_query.get(target_transformation.select.label_alias),
            "distinct": column_query.get(target_transformation.select.distinct_alias),
            "value": column_query.get(target_transformation.select.value_alias),
            "select": prepped_inner_select_node,
            "where": column_query.get(target_transformation.select.where_alias),
        }
        if when := column_query.get(target_transformation.select.whens_alias):
            when_items = []
            for when_item in when:
                when_items.append(
                    {
                        "when": when_item.get(
                            target_transformation.select.when_node.when_alias
                        ),
                        "then": when_item.get(
                            target_transformation.select.when_node.then_alias
                        ),
                    }
                )
            updated_column_query["when"] = when_items
        if else_ := column_query.get(target_transformation.select.else_alias):
            updated_column_query["else_"] = self._process_select_transformation(
                else_, select_alias, target_transformation
            )

        keys_to_pop = []
        if len(updated_column_query.get("select", {}).keys()) == 0:
            keys_to_pop.append("select")

        for key, value in updated_column_query.items():
            if value is None:
                keys_to_pop.append(key)

        for key_to_pop in keys_to_pop:
            updated_column_query.pop(key_to_pop)

        return cast(HqlSelect, updated_column_query)

    def find_transformation(self, hql_query: HqlQuery) -> Union[QueryTransformation, None]:
        """
        This function can be overriden if users need to identify their transformation map using a non-standard method.
        :param hql_query: HqlQuery
        :return:
        """
        if len(self._transformations) == 0:
            return None

        query_keys = hql_query.keys()
        for transformation_name, transformation in self._transformations.items():
            hits = 0
            for field in list(transformation.__dict__.keys()):
                query_field = getattr(transformation, field)
                if hasattr(query_field, "alias"):
                    query_field_alias = query_field.alias
                    for key in query_keys:
                        if key == query_field_alias:
                            hits += 1

            if hits == len(query_keys):
                return transformation

        return None

    def _process_filter_transformation(
        self, where: WhereClausT, query_transformation: QueryTransformation
    ):
        keys = where.keys()
        if len(keys) == 0:
            return {}

        return_dict = {}
        for key in keys:
            lower_cased_key = key.lower()
            if lower_cased_key == query_transformation.filter_info.and_alias:
                return_dict["and"] = where[key]

            elif lower_cased_key == query_transformation.filter_info.or_alias:
                value = where[key]
                or_clause_input = []
                for or_dict in value:
                    or_clause_input.append(
                        self._process_filter_transformation(or_dict, query_transformation)
                    )
                return_dict["or"] = or_clause_input

            else:
                original_key = key
                operator_start_index = key.find("__")
                user_operator_string = key[operator_start_index + 2 :]
                conversion = query_transformation.filter_info.operator_map.get(
                    user_operator_string, None
                )
                if conversion is not None:
                    key = key.replace(f"__{user_operator_string}", f"__{conversion}")

                return_dict[key] = where[original_key]

        return return_dict
