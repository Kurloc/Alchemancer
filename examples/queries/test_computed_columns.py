test_query = {
    "name": "test_subqueries",
    "query": {
        "select": {
            "User": {
                "id": {},
                "name": {},
                "date_create.__add__(cast('100 DAYS', INTERVAL))": {  # <-- This does not work in AMDQL 1.0
                    "label": "date_created_plus_100_days",
                },
            }
        },
        "limit": 5,
    },
    "expected_sql": """
SELECT user_account.id,
       user_account.name,
       user_account.date_create + cast(:param_1 as interval) as date_created_plus_100_days
FROM   user_account limit :param_2
    """,
}
