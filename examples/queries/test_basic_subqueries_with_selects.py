test_query = {
    "name": "test_basic_subqueries_with_selects",
    "query": {
        "subqueries": {
            "UsersOver100": {
                "select": {"User": {"id": {}, "name": {}, "account_balance": {}}},
                "where": {"User.account_balance__GT": 100},
            }
        },
        "select": {
            "UsersOver100": {
                "user_count": {
                    "select": "count(id)",
                    "where": {
                        "UsersOver100.name__LIKE": "%A%",
                        "UsersOver100.id__NE": 5,
                    },
                },
            }
        },
        "limit": 5,
    },
    "expected_sql": """
SELECT 
    count(anon_2.id) 
    FILTER (WHERE anon_2.name LIKE :name_1 AND anon_2.id != :id_1) AS anon_1 
FROM (
    SELECT 
    user_account.id AS id,
    user_account.name AS name,
    user_account.account_balance AS account_balance 
FROM user_account 
WHERE user_account.account_balance > :account_balance_1) AS anon_2
LIMIT :param_1
    """,
}
