import os
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List, Tuple

import pytest
from sqlalchemy import Engine, insert, select, text
from sqlalchemy_utils import create_database, database_exists

from alchemancer.query_generator import QueryGenerator
from alchemancer.reflection_handler import ReflectionHandler
from tests.fixtures.models.base_model import BaseModel
from tests.fixtures.models.role import Role
from tests.fixtures.models.user import User
from tests.fixtures.test_dbs import psql_engine, sqlite_engine

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

BaseModel.metadata.create_all(psql_engine)
BaseModel.metadata.create_all(sqlite_engine)
ReflectionHandler().init(
    [
        (
            "tests.fixtures.models",
            Path.joinpath(
                Path(__file__).parent.parent,  # suite dir  # tests dir
                f"fixtures{os.sep}models",
            ),
        ),
    ],
    [
        (
            "examples.resolvers",
            Path.joinpath(
                (Path(__file__).parent.parent.parent),
                f"examples{os.sep}resolvers",
            ),
        )
    ],
)

test_cases = [
    (x["name"], x)
    for x in ReflectionHandler._import_modules_from_path(
        str(
            Path.joinpath(
                (Path(__file__).parent.parent.parent),  # suite dir  # tests dir
                "examples/queries",
            )
        ),
        "examples.queries",
        [dict],
        check_subclasses_of_type=False,
        return_instances=True,
    )
]


@pytest.mark.parametrize(
    "name,test_dict,seed_data,engine",
    [
        (
            "simple_return_sqlite",
            {
                "select": {
                    "User": {
                        "id": {},
                    }
                }
            },
            [(User, {"id": 1, "name": "John"})],
            sqlite_engine,
        ),
        (
            "simple_return_postgres",
            {
                "select": {
                    "User": {
                        "array_agg(id)": {},
                    }
                }
            },
            [(User, {"name": "John"})],
            psql_engine,
        ),
    ],
)
def test_query(name, test_dict: Dict, seed_data: List[Tuple[Any, Dict]], engine: Engine):
    with engine.connect() as testing_connection:
        for d in seed_data:
            testing_connection.execute(insert(d[0]).values(**d[1]))
            testing_connection.commit()

    query = QueryGenerator(engine).return_from_hql_query(test_dict)


def test_subquery():
    with psql_engine.connect() as testing_connection:
        testing_connection.execute(
            insert(User).values(
                [
                    {
                        "name": "JohnA",
                        "account_balance": 100,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnB",
                        "account_balance": 101,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnC",
                        "account_balance": 102,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnD",
                        "account_balance": 103,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnE",
                        "account_balance": 104,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnAB",
                        "account_balance": 200,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnBC",
                        "account_balance": 201,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnCD",
                        "account_balance": 202,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnDE",
                        "account_balance": 203,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                    {
                        "name": "JohnEF",
                        "account_balance": 204,
                        "account_details": {"testing": {"inner": [1, 2, 3]}},
                    },
                ]
            )
        )
        testing_connection.commit()

        column_with_json = User.account_details
        accessor_chain = ["testing", "inner"]
        for item in accessor_chain:
            column_with_json = column_with_json[item]

        users_over_100 = (
            select(User.name, User.account_balance, column_with_json.label("testing"))
            .where(User.account_balance > 99, User.account_balance < 300)
            .subquery()
        )
        users_over_100_with_a_in_name = select(
            users_over_100.c.name,
            users_over_100.c.account_balance,
            users_over_100.c.testing,
        ).where(users_over_100.c.name.like("%A%"))

        print(users_over_100_with_a_in_name)
        results = testing_connection.execute(users_over_100_with_a_in_name)
        print(results.fetchall())


def test_cte():
    # query in sqlalchemy
    cte = select(Role.id, Role.name, Role.parent_role_id)
    union_cte = cte.union_all(
        select(cte.c.id, cte.c.name, Role.id).join(Role, Role.id == cte.c.parent_role_id)
    ).cte(recursive=True, name="roles_base_cte")

    # query in json
    x = {
        "select": {"union_query": {"id": {}, "name": {}}},
        "union_all": {
            "name": "union_query",
            "left": {
                "select": {
                    "Role": {
                        "id": {},
                        "name": {},
                        "parent_role_id": {},
                    }
                },
                "cte": {
                    "recursive": True,
                    "name": "cte_base",
                },
            },
            "right": {
                "select": {
                    "cte_base": {
                        "id": {},
                        "name": {},
                    }
                },
                "join": {
                    "Role": {
                        "select": {"id": {}},
                        "where": {"Role.id__EQ": "cte_base.parent_role_id"},
                    }
                },
            },
        },
    }
    # query in sql
    # WITH RECURSIVE roles_base_cte(id, name, parent_role_id) AS
    #                    (SELECT role.id AS id, role.name AS name, role.parent_role_id AS parent_role_id
    #                     FROM role
    #                     UNION ALL
    #                     SELECT
    #                         anon_1.id AS id,
    #                         anon_1.name AS name,
    #                         role.id AS id_1
    #                     FROM (
    #                         SELECT role.id AS id, role.name AS name,
    #                                role.parent_role_id AS parent_role_id
    #                           FROM role
    #                     ) AS anon_1
    #                     JOIN role ON role.id = anon_1.parent_role_id)
    # SELECT DISTINCT roles_base_cte.id, roles_base_cte.name, roles_base_cte.parent_role_id
    # FROM roles_base_cte

    # with psql_engine.connect() as testing_connection:
    #     testing_connection.execute(
    #         insert(User).values(
    #             [
    #                 {"name": "JohnA", "account_balance": 100, "account_details": {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnB", "account_balance": 101, "account_details": {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnC", "account_balance": 102, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnD", "account_balance": 103, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnE", "account_balance": 104, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnAB", "account_balance": 200, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnBC", "account_balance": 201, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnCD", "account_balance": 202, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnDE", "account_balance": 203, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #                 {"name": "JohnEF", "account_balance": 204, "account_details":  {"testing": {"inner": [1,2,3]}}},
    #             ]
    #         )
    #     )
    #     testing_connection.commit()
    #
    #     column_with_json = User.account_details
    #     accessor_chain = ["testing", "inner"]
    #     for item in accessor_chain:
    #         column_with_json = column_with_json[item]
    #
    #     users_over_100 = (
    #         select(User.name, User.account_balance, column_with_json.label("testing"))
    #         .where(User.account_balance > 99, User.account_balance < 300)
    #         .subquery()
    #     )
    #     users_over_100_with_a_in_name = select(
    #         users_over_100.c.name, users_over_100.c.account_balance, users_over_100.c.testing
    #     ).where(users_over_100.c.name.like("%A%"))
    #
    #     print(users_over_100_with_a_in_name)
    #     results = testing_connection.execute(users_over_100_with_a_in_name)
    #     print(results.fetchall())


def test_resolver_results():
    query_results = QueryGenerator(psql_engine).return_from_hql_query(
        {
            "select": {
                "RecursiveRolesResolver()": {
                    "role_id": {},
                    "role_name": {},
                    "role_parent_id": {},
                }
            },
            "resolver_args": {"role_id": 1},
        }
    )
    pprint(query_results)
