import os
from pathlib import Path
from typing import Dict

import pytest
from sql_formatter.core import format_sql
from sqlalchemy.dialects.postgresql import aggregate_order_by

from alchemancer.sqlalchemy.query_generator import QueryGenerator
from alchemancer.sqlalchemy.reflection_handler import ReflectionHandler
from tests.fixtures.test_dbs import psql_engine

ReflectionHandler().init(
    [(
        "tests.fixtures.models",
        Path.joinpath(
            (
                Path(__file__)
                .parent  # suite dir
                .parent  # tests dir
            ),
            f"fixtures{os.sep}models"
        ),
    )]
)

test_cases = [(x['name'], x) for x in ReflectionHandler._import_modules_from_path(
    str(Path.joinpath(
        (
            Path(__file__)
            .parent  # suite dir
            .parent  # tests dir
            .parent
        ),
        f"examples/queries"
    )),
    'examples.queries',
    [dict],
    check_subclasses_of_type=False,
    return_instances=True
)]


@pytest.mark.parametrize("name,test_dict", test_cases)
def test_query(name, test_dict: Dict):
    query = QueryGenerator(psql_engine, {'aggregate_order_by': aggregate_order_by})._process_query(test_dict['query'])
    print()
    print('TEST', name)
    print('EXPECTED', '\n', format_sql(test_dict['expected_sql']), '\n')
    print('OUTPUT', '\n', format_sql(str(query.query)))
    assert format_sql(str(query.query)) == format_sql(test_dict['expected_sql'])
