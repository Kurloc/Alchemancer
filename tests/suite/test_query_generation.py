import os
from pathlib import Path
from typing import Dict

import pytest
from sql_formatter.core import format_sql
from sqlalchemy import func, over
from sqlalchemy.dialects.postgresql import INTERVAL, aggregate_order_by

from alchemancer.query_generator import QueryGenerator
from alchemancer.reflection_handler import ReflectionHandler
from examples.resolvers.roles_resolver import RecursiveRolesResolver
from tests.fixtures.test_dbs import psql_engine

ReflectionHandler().init(
    [
        (
            "tests.fixtures.models",
            Path.joinpath(
                Path(__file__).parent.parent,
                f"fixtures{os.sep}models",
            ),
        )
    ],
    [
        (
            "examples.resolvers",
            Path.joinpath(
                Path(__file__).parent.parent.parent,
                f"examples{os.sep}resolvers",
            ),
        )
    ],
)

test_cases = [
    (x["name"], x)
    for x in ReflectionHandler._import_objects_from_modules_via_path(
        str(
            Path.joinpath(
                Path(__file__).parent.parent.parent,  # suite dir  # tests dir
                "examples/queries",
            )
        ),
        "examples.queries",
        dict,
        check_subclasses_of_type=False,
        return_instances=True,
    )
]


@pytest.mark.parametrize("name,test_dict", test_cases)
def test_query(name, test_dict: Dict):
    print(RecursiveRolesResolver().name)
    ReflectionHandler().init(
        [
            (
                "tests.fixtures.models",
                Path.joinpath(
                    Path(__file__).parent.parent,
                    f"fixtures{os.sep}models",
                ),
            )
        ],
        [
            (
                "examples.resolvers",
                Path.joinpath(
                    Path(__file__).parent.parent.parent,
                    f"examples{os.sep}resolvers",
                ),
            )
        ],
    )
    expected_sql = test_dict["expected_sql"]
    query = QueryGenerator(
        psql_engine,
        {
            "aggregate_order_by": aggregate_order_by,
            "lag": func.lag,
            "lead": func.lead,
            "over": over,
            "INTERVAL": INTERVAL,
            "cast": func.cast,
            "count": func.count,
        },
    )._process_query(test_dict["query"])
    print()
    print("TEST", name)
    print("EXPECTED", "\n", format_sql(expected_sql), "\n")
    print("OUTPUT", "\n", format_sql(str(query.query)))
    assert format_sql(str(query.query)) == format_sql(test_dict["expected_sql"])
