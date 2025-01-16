import os
from pathlib import Path

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

def test_ast_functions():
    token = QueryGenerator(psql_engine)._build_ast_tokens(
        "coalesce(coalesce(array_agg(User.id), '0'), 0)"
    )
    assert str(token) == "coalesce(coalesce(array_agg(user_account.id), :coalesce_1), :coalesce_2)"
