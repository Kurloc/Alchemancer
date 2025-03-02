test_query = {
    "name": "test_functions_advanced",
    "query": {
        "select": {
            "User": {
                "array_agg(aggregate_order_by(User.id, coalesce(User.account_balance, 0).desc()))": {
                    "label": "ordered_ids"
                },
                "array_agg(aggregate_order_by(coalesce(User.account_balance, 0), coalesce(User.account_balance, 0).desc()))": {
                    "label": "ordered_balances"
                }
            }
        },
        "where": {
            "or": [
                {"or": [
                    {"User.id__EQ": 1},
                    {"User.id__EQ": 2}
                ]},
                {"or": [
                    {"User.id__EQ": 3},
                    {"User.id__EQ": 4},
                ]},
            ],
            "User.id__NE": 5
        },
        "limit": 5,
        "offset": 10,
        "order_by": {
            "User.id": {
                "index": 0,
                "dir": "desc"
            }
        },
        "group_by": [
            "User.id",
            "User.account_balance"
        ],
    },
    "expected_sql": """
SELECT array_agg(user_account.id ORDER BY coalesce(user_account.account_balance, %(coalesce_1)s) desc) as ordered_ids,
       array_agg(coalesce(user_account.account_balance, %(coalesce_2)s) ORDER BY coalesce(user_account.account_balance, %(coalesce_3)s) desc) as ordered_balances
FROM   user_account
WHERE  (user_account.id = :id_1
    or user_account.id = :id_2
    or user_account.id = :id_3
    or user_account.id = :id_4)
   and user_account.id != :id_5
GROUP BY user_account.id, user_account.account_balance
ORDER BY user_account.id desc limit :param_1 offset :param_2
    """
}
