test_query = {
    "name": "testing exists interface",
    "query": {
        "subqueries": {
            "subq1": {
                "select": {
                    "User": {
                        "id": {},
                    }
                },
                "where": {"User.fullname__EQ": "toast"},
            }
        },
        "select": {"User": {"id": {}}},
        "where": {"subq1__exists": {}, "User.id__EQ": 2},
    },
    "expected_sql": """
SELECT user_account.id
FROM   user_account
WHERE  (exists (SELECT user_account.id
                FROM   user_account
                WHERE  user_account.fullname = :fullname_1))
   and user_account.id = :id_1
    """,
}
