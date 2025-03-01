test_query = {
    "name": "test_json_selects_top_level",
    "query": {
        "select": {
            "User": {
                "id": {},
                "fullname": {},
                "account_details['test']['inner']": {}
            }
        }
    },
    "expected_sql": """
 SELECT user_account.id,
       user_account.fullname,
       user_account.account_details[:account_details_1][:param_1] as anon_1
FROM   user_account
    """,
}
