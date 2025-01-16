test_query = {
    "name": "test_the_basics",
    "query": {
        "select": {
            "User": {
                "id": {},
                "name": {}
            }
        },
        "joins": {
            "Address": {
                "select": {
                    "id": {}
                },
                "where": {
                    "Address.user_id__EQ": "User.id"
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
        ],
        "distinct": True
    },
    "expected_sql": """
SELECT DISTINCT user_account.id,
                user_account.name,
                address.id as address_id
FROM   user_account join address
        ON address.user_id = user_account.id
WHERE  (user_account.id = :id_1
    or user_account.id = :id_2
    or user_account.id = :id_3
    or user_account.id = :id_4)
   and user_account.id != :id_5
GROUP BY user_account.id
ORDER BY user_account.id desc limit :param_1 offset :param_2
    """
}
