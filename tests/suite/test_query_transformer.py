from pprint import pprint
from typing import Dict

import pytest

from alchemancer.query_transformation_handler import (
    DebugNode,
    DistinctNode,
    FilterNode,
    GroupByNode,
    HavingClauseNode,
    HqlCTENode,
    HqlUnionNode,
    JoinNode,
    LimitNode,
    OffsetNode,
    OrderByNode,
    QueryTransformation,
    QueryTransformationHandler,
    ResolverArgsNode,
    SelectNode,
    SortItemNode,
    WhenThenNode,
    WhereClauseNode,
)
from alchemancer.types.query import HqlQuery

sample_query = {
    "query": {"User": {"id": {}, "name": {}}},
    "joins": {"Address": {"selects": {"id": {}}, "where": {"Address.user_id__EQ": "User.id"}}},
    "where": {
        "or": [
            {"or": [{"User.id__EQ": 1}, {"User.id__EQ": 2}]},
            {
                "or": [
                    {"User.id__EQ": 3},
                    {"User.id__EQ": 4},
                ]
            },
        ],
        "User.id__NE": 5,
    },
    "limit": 5,
    "offset": 10,
    "order_by": {"User.id": {"index": 0, "dir": "desc"}},
    "group_by": [
        "User.id",
    ],
    "distinct": True,
}


@pytest.mark.parametrize(
    "query,transformation,expected_query",
    [
        [
            sample_query,
            QueryTransformation(
                SelectNode(
                    when_node=WhenThenNode("wheres", "value"),
                    alias="query",
                    label_alias="label",
                    value_alias="value",
                    distinct_alias="distinct",
                    whens_alias="whens",
                    else_alias="else_",
                    select_alias="select",
                    where_alias="where",
                ),
                JoinNode(
                    alias="joins",
                    select_node=SelectNode(
                        when_node=WhenThenNode("wheres", "value"),
                        alias="query",
                        label_alias="label",
                        value_alias="value",
                        distinct_alias="distinct",
                        whens_alias="whens",
                        else_alias="else_",
                        select_alias="selects",
                        where_alias="where",
                    ),
                ),
                WhereClauseNode(
                    alias="where",
                ),
                HavingClauseNode(
                    alias="having",
                ),
                FilterNode(),
                LimitNode(
                    alias="limit",
                ),
                OffsetNode(
                    alias="offset",
                ),
                OrderByNode(
                    alias="order_by",
                    sort_node=SortItemNode(
                        index_alias="index",
                        nulls_last_alias="nulls_last",
                        dir_alias="dir",
                        asc_alias="asc",
                        desc_alias="desc",
                    ),
                ),
                GroupByNode(
                    alias="group_by",
                ),
                DistinctNode(
                    alias="distinct",
                ),
                HqlCTENode(
                    name_alias="name",
                    recursive_alias="recursive",
                ),
                HqlUnionNode(
                    alias="union_all",
                ),
                HqlUnionNode(
                    alias="union_all",
                ),
                ResolverArgsNode(
                    alias="resolver_args",
                ),
                DebugNode(
                    alias="debug",
                    html_alias="html",
                    str_alias="str",
                ),
            ),
            {
                "select": {"User": {"id": {}, "name": {}}},
                "joins": {
                    "Address": {
                        "select": {"id": {}},
                        "where": {"Address.user_id__EQ": "User.id"},
                    }
                },
                "where": {
                    "or": [
                        {"or": [{"User.id__EQ": 1}, {"User.id__EQ": 2}]},
                        {
                            "or": [
                                {"User.id__EQ": 3},
                                {"User.id__EQ": 4},
                            ]
                        },
                    ],
                    "User.id__NE": 5,
                },
                "limit": 5,
                "offset": 10,
                "order_by": {"User.id": {"index": 0, "dir": "desc"}},
                "group_by": [
                    "User.id",
                ],
                "distinct": True,
            },
        ],
        [
            {
                "🤏": {"User": {"id": {}, "name": {}}},
                "👉👈": {
                    "Address": {"🤏": {"id": {}}, "🔎": {"Address.user_id__↔️": "User.id"}}
                },
                "🔎": {
                    "⏸️": [
                        {"⏸️": [{"User.id__↔️": 1}, {"User.id__↔️": 2}]},
                        {
                            "⏸️": [
                                {"User.id__↔️": 3},
                                {"User.id__↔️": 4},
                            ]
                        },
                    ],
                    "User.id__❗↔️": 5,
                },
                "🚧": 5,
                "⚖️": 10,
                "☰": {"User.id": {"🎯": 0, "➡️": "⬇️"}},
                "🔗": [
                    "User.id",
                ],
                "🌟": True,
            },
            QueryTransformation(
                SelectNode(
                    when_node=WhenThenNode("when", "value"),
                    alias="🤏",
                    label_alias="label",
                    value_alias="value",
                    distinct_alias="distinct",
                    whens_alias="whens",
                    else_alias="else_",
                    select_alias="🤏",
                    where_alias="🔎",
                ),
                JoinNode(
                    alias="👉👈",
                    select_node=SelectNode(
                        when_node=WhenThenNode("when", "value"),
                        alias="query",
                        label_alias="label",
                        value_alias="value",
                        distinct_alias="distinct",
                        whens_alias="whens",
                        else_alias="else_",
                        select_alias="🤏",
                        where_alias="🔎",
                    ),
                ),
                WhereClauseNode(
                    alias="🔎",
                ),
                HavingClauseNode(
                    alias="✊",
                ),
                FilterNode(
                    or_alias="⏸️",
                    and_alias="➕",
                    operator_map={
                        "↔️": "EQ",
                        "❗↔️": "NE",
                    },
                ),
                LimitNode(
                    alias="🚧",
                ),
                OffsetNode(
                    alias="⚖️",
                ),
                OrderByNode(
                    alias="☰",
                    sort_node=SortItemNode(
                        index_alias="🎯",
                        nulls_last_alias="nulls_last",
                        dir_alias="➡️",
                        asc_alias="⬆️",
                        desc_alias="⬇️",
                    ),
                ),
                GroupByNode(
                    alias="🔗",
                ),
                DistinctNode(
                    alias="🌟",
                ),
                HqlCTENode(
                    name_alias="name",
                    recursive_alias="recursive",
                ),
                HqlUnionNode(
                    alias="union_all",
                ),
                HqlUnionNode(
                    alias="union_all",
                ),
                ResolverArgsNode(
                    alias="resolver_args",
                ),
                DebugNode(
                    alias="debug",
                    html_alias="html",
                    str_alias="str",
                ),
            ),
            {
                "select": {"User": {"id": {}, "name": {}}},
                "joins": {
                    "Address": {
                        "select": {"id": {}},
                        "where": {"Address.user_id__EQ": "User.id"},
                    }
                },
                "where": {
                    "or": [
                        {"or": [{"User.id__EQ": 1}, {"User.id__EQ": 2}]},
                        {
                            "or": [
                                {"User.id__EQ": 3},
                                {"User.id__EQ": 4},
                            ]
                        },
                    ],
                    "User.id__NE": 5,
                },
                "limit": 5,
                "offset": 10,
                "order_by": {"User.id": {"index": 0, "dir": "desc"}},
                "group_by": [
                    "User.id",
                ],
                "distinct": True,
            },
        ],
    ],
)
def test_query_transformer(
    query: Dict, transformation: QueryTransformation, expected_query: HqlQuery
):
    query_transformer = QueryTransformationHandler({"test_transformation": transformation})

    output_query = query_transformer.transform_query(query)
    print("\n=== OUTPUT QUERY ===")
    pprint(output_query)
    print("=== EXPECTED QUERY ===")
    pprint(expected_query)

    assert output_query == expected_query
