import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy_utils import create_database, database_exists

from alchemancer import ReflectionHandler
from tests.fixtures.models.generic.base_model import BaseModel
from tests.fixtures.models.postgresql.psql_base_model import PsqlBaseModel
from tests.fixtures.test_dbs import psql_engine, sqlite_engine


def init_test_suite():
    """
    Runs once for the entire test module
    :return:
    """
    if not database_exists(psql_engine.url):
        create_database(psql_engine.url)
    else:
        with psql_engine.connect() as connection:
            connection.execute(
                text(
                    """
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;"""
                )
            )
            connection.commit()

    ReflectionHandler().init(
        [
            (
                "tests.fixtures.models.generic",
                Path.joinpath(Path(__file__).parent, "models", "generic"),
            ),
            (
                "tests.fixtures.models.postgresql",
                Path.joinpath(Path(__file__).parent, "models", "postgresql"),
            ),
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

    BaseModel.metadata.create_all(psql_engine)
    BaseModel.metadata.create_all(sqlite_engine)

    # Create models for PSQL specific test
    PsqlBaseModel.metadata.create_all(psql_engine)


init_test_suite()
