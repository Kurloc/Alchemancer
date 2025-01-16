test_query = {
    "name": "test_subqueries",
    "query": {
        "subqueries": {
            "UsersOver100": {
                "select": {"User": {"id": {}, "name": {}, "account_balance": {}}},
                "where": {"User.account_balance__GT": 100},
            }
        },
        "select": {
            "UsersOver100": {
                "id": {},
                "name": {},
                "account_balance": {},
            }
        },
        "where": {
            "UsersOver100.name__LIKE": "%A%",
            "UsersOver100.id__NE": 5,
        },
        "limit": 5,
    },
    "expected_sql": """
SELECT anon_1.id,
       anon_1.name,
       anon_1.account_balance
FROM   (SELECT user_account.id as id,
               user_account.name as name,
               user_account.account_balance as account_balance
        FROM   user_account
        WHERE  user_account.account_balance > :account_balance_1) as anon_1
WHERE  anon_1.name like :name_1
   and anon_1.id != :id_1 limit :param_1
    """,
}
