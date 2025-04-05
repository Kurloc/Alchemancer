from pathlib import Path

from sqlalchemy import insert, select

from alchemancer.reflection_handler import ReflectionHandler
from tests.fixtures.models.user import User
from tests.fixtures.test_dbs import psql_engine

test_cases = [
    (x["name"], x)
    for x in ReflectionHandler._import_objects_from_modules_via_path(
        str(
            Path.joinpath(
                (Path(__file__).parent.parent.parent),  # suite dir  # tests dir
                "examples/queries",
            )
        ),
        "examples.queries",
        dict,
        check_subclasses_of_type=False,
        return_instances=True,
    )
]


def test_json_querying():
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
