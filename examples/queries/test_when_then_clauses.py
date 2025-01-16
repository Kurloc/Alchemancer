test_query = {
    "name": "test_when_then_clauses",
    "query": {
        "select": {
            "User": {
                "id": {},
                "email": {
                    "whens": [
                        {"when": {"User.id__EQ": 1}, "then": "email_#1@email.com"},
                        {"when": {"User.id__EQ": 2}, "then": "email_#2@email.com"},
                        {"when": {"User.id__EQ": 3}, "then": "User.id"},
                    ],
                    "else_": "User.id",
                },
            }
        },
        "where": {
            "or": [
                {"or": [{"User.id__EQ": 1}, {"User.id__EQ": 2}]},
                {
                    "or": [
                        {"User.id__EQ": 3},
                        {"User.id__EQ": 4},
                    ]
                },
            ],
            "User.id__NE": 5,
        },
        "limit": 5,
        "offset": 10,
        "order_by": {"User.id": {"index": 0, "dir": "desc"}},
        "group_by": [
            "User.id",
        ],
        "distinct": True,
    },
    "expected_sql": """
SELECT DISTINCT user_account.id,
                case when :param_1 then :param_2
                     when :param_3 then :param_4
                     when :param_5 then user_account.id
                     else user_account.id end as anon_1
FROM   user_account
WHERE  (user_account.id = :id_1
    or user_account.id = :id_2
    or user_account.id = :id_3
    or user_account.id = :id_4)
   and user_account.id != :id_5
GROUP BY user_account.id
ORDER BY user_account.id desc limit :param_6 offset :param_7
    """,
}
