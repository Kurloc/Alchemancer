from alchemancer.types.query import HqlQuery

test_query = {
    "name": "testing not exists interface",
    "query": HqlQuery(
        select={"User": {"id": {}}},
        subqueries={
            "subq1": HqlQuery(
                select={
                    "User": {
                        "id": {},
                    }
                },
                where={"User.fullname__EQ": "toast"},
            )
        },
        where={"subq1__not_exists": {}, "User.id__EQ": 2},
    ),
    "expected_sql": """
SELECT user_account.id
FROM   user_account
WHERE  not (exists (SELECT user_account.id
                    FROM   user_account
                    WHERE  user_account.fullname = :fullname_1))
   and user_account.id = :id_1
    """,
}
